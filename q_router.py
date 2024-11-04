""" Q.Conveyor (desktop/mobile)

Prerequisites:
    * Have a Python 3 environment available to you (possibly by using a
      virtual environment: https://virtualenv.pypa.io/en/stable/).
    * Run pip install -r requirements.txt --user with this directory.
      or
      Run pip install -r requirements.txt with this directory as your root.

    * Copy q_industrialist_settings.py.template into q_industrialist_settings.py and
      mood for your needs.
    * Copy q_conveyor_settings.py.template into q_conveyor_settings.py and
      mood for your needs.
    * Create an SSO application at developers.eveonline.com with the scopes
      from g_client_scope list declared in q_industrialist_settings.py and the
      callback URL "https://localhost/callback/".
      Note: never use localhost as a callback in released applications.

To run this example, make sure you have completed the prerequisites and then
run the following command from this directory as the root:

$ chcp 65001 & @rem on Windows only!
$ python eve_sde_tools.py --cache_dir=~/.q_industrialist
$ python q_router.py --corporation="R Industry" --corporation="R Strike" --online --cache_dir=~/.q_industrialist

Requires application scopes:
    * esi-industry.read_corporation_jobs.v1 - Requires role(s): Factory_Manager
    * esi-assets.read_corporation_assets.v1 - Requires role(s): Director
    * esi-corporations.read_blueprints.v1 - Requires role(s): Director
"""
import typing
import re

import console_app
import q_industrialist_settings
import q_conveyor_settings
import q_router_settings
import render_html_conveyor_db

import postgresql_interface as db
import eve_router_tools as tools

from __init__ import __version__


def main():
    # работа с параметрами командной строки, получение настроек запуска программы
    argv_prms = console_app.get_argv_prms(['corporation='])

    if not argv_prms["corporation"]:
        console_app.print_version_screen()
        console_app.print_help_screen(0)
        return

    qidb: db.QIndustrialistDatabase = db.QIndustrialistDatabase("router", debug=argv_prms.get("verbose_mode", False))
    qidb.connect(q_industrialist_settings.g_database)
    qit: db.QSwaggerTranslator = db.QSwaggerTranslator(qidb)
    qid: db.QSwaggerDictionary = db.QSwaggerDictionary(qit)
    # загрузка справочников
    qid.load_market_groups()
    qid.load_universe_categories()
    qid.load_universe_groups()
    qid.load_all_known_type_ids()
    qid.load_blueprints()
    qid.load_conveyor_best_formulas()
    # загрузка информации, связанной с корпорациями
    for corporation_name in argv_prms['corporation']:
        # публичные сведения (пилоты, структуры, станции, корпорации)
        corporation: db.QSwaggerCorporation = qid.load_corporation(corporation_name)
        # загрузка корпоративных ассетов
        qid.load_corporation_assets(corporation, load_unknown_type_assets=True, load_asseted_blueprints=True)
        qid.load_corporation_blueprints(corporation, load_unknown_type_blueprints=True)
        qid.load_corporation_blueprints_undelivered(corporation)
        qid.load_corporation_container_places(corporation)
        qid.load_corporation_industry_jobs_active(corporation, load_unknown_type_blueprints=True)
        qid.load_corporation_industry_jobs_completed(corporation, load_unknown_type_blueprints=True)
        qid.load_corporation_orders_active(corporation)
        qid.load_corporation_stations(corporation)
    # загрузка настроек работы конвейера (редактируются online через php_interface)
    qid.load_conveyor_limits()
    qid.load_conveyor_requirements()
    # загрузка информации об обновлении сведений в БД для загруженных корпораций
    qid.load_lifetime(list(qid.corporations.keys()))
    # загружаем сведения о станциях, которые есть в настройках маршрутизатора
    for r in q_router_settings.g_routes:
        station: typing.Optional[db.QSwaggerStation] = qid.load_station_by_name(r['station'])
        if not station:
            raise Exception(f"Unable to load station by name: {r['station']}")
    # загрузка conveyor-формул после загрузки всех справочных и корпоративных данных (в т.ч. станций)
    qid.load_conveyor_formulas(only_for_active_hubs=True)
    # отключаемся от сервера
    qid.disconnect_from_translator()
    del qit
    qidb.disconnect()
    del qidb

    # следуем по загруженным данным и собираем входные данные (настройки) маршрутизации продуктов производства
    settings_of_router: typing.List[tools.RouterSettings] = []
    for r in q_router_settings.g_routes:
        # инициализируем настройки маршрутизации продуктов производства
        settings: tools.RouterSettings = tools.RouterSettings()
        settings.station = r['station']
        settings.desc = r['desc']
        settings.cached_output = qid.get_type_ids_by_params(
            r.get('output_types', []),
            r.get('output_groups', []),
            r.get('output_categories', []),
            r.get('output_market_groups', []),
            r.get('except_output_types', []))
        settings.output = list(settings.cached_output.keys())
        settings_of_router.append(settings)

    # проверка конфликтных ситуаций (никакой продукт не может быть упомянут дважды на разных станциях)
    unique_manuf_lines: typing.Set[int] = set()
    for settings in settings_of_router:
        for p in settings.output:
            if p in unique_manuf_lines:
                raise Exception(f"Unable to add manuf product twice: product #{p} to {settings.station}")
            unique_manuf_lines.add(p)
    del unique_manuf_lines

    # следуем по загруженным данным и собираем входные данные (настройки) запуска алгоритма конвейера
    settings_of_conveyors: typing.List[tools.ConveyorSettings] = []
    for entity in q_conveyor_settings.g_entities:
        # пропускаем отключенные группы настроек (остались для архива?)
        if not entity.get('enabled', False) or not entity.get('conveyors'):
            continue
        # собираем список корпораций к которым относятся настройки
        industry_corporation_name: str = entity.get('corporation')
        if industry_corporation_name:
            corporation: db.QSwaggerCorporation = qid.get_corporation_by_name(industry_corporation_name)
            if not corporation:
                continue
            corporation_ids: typing.List[int] = [corporation.corporation_id]
        else:
            corporation_ids: typing.List[int] = [corporation_id for corporation_id in qid.corporations.keys()]
        # собираем списки контейнеров, к которым относятся настройки
        for conveyor in entity['conveyors']:
            # пропускаем некорректные настройки (просто правильность синтаксиса настроек),
            # например, если есть раздел 'reactions', то в нём должен быть подраздел 'formulas'
            if not conveyor.get('blueprints'):
                continue
            if conveyor.get('reactions') and not conveyor['reactions'].get('formulas'):
                continue
            # собираем список корпоративных контейнеров по указанным названиям
            for corporation_id in corporation_ids:
                corporation = qid.get_corporation(corporation_id)
                # инициализируем настройки запуска конвейера
                settings: tools.ConveyorSettings = tools.ConveyorSettings(corporation)
                activities: typing.List[str] = conveyor.get('activities', ['manufacturing'])
                # читаем настройки производственной активности
                settings.fixed_number_of_runs = conveyor.get('fixed_number_of_runs', None)
                settings.same_stock_container = conveyor.get('same_stock_container', True)
                settings.activities = [db.QSwaggerActivityCode.from_str(a) for a in activities]
                settings.conveyor_with_reactions = conveyor.get('reactions', False)
                # получаем информацию по реакциям (если включены)
                for container_id in corporation.container_ids:
                    container: db.QSwaggerCorporationAssetsItem = corporation.assets.get(container_id)
                    if not container:
                        continue
                    container_name: str = container.name
                    if not container_name:
                        continue
                    # проверяем, что контейнер лежит в ангаре станции (а не в карго джампака)
                    container_hangar: str = container.location_flag
                    if container_hangar[:-1] != 'CorpSAG':
                        continue
                    # проверяем, что принадлежность контейнера станции выяснить можно (из ассетов пропадают офисы)
                    if not container.station_id:
                        container = container
                        continue
                    # определяем признаки категорий, к которым принадлежала коробка
                    source_box: bool = False
                    stock_box: bool = False
                    formulas_box: bool = False
                    output_box: bool = False
                    exclude_box: bool = False
                    # превращаем названия (шаблоны названий) в номера контейнеров
                    for priority in conveyor['blueprints'].keys():
                        if next((1 for tmplt in conveyor['blueprints'][priority] if re.search(tmplt, container_name)), None):
                            scs = tools.ConveyorSettingsPriorityContainer(priority, settings, corporation, container)
                            settings.containers_sources.append(scs)
                            source_box = True
                            if settings.same_stock_container:
                                scs = tools.ConveyorSettingsContainer(settings, corporation, container)
                                settings.containers_stocks.append(scs)
                                stock_box = True
                            break
                    if not settings.same_stock_container:
                        if next((1 for tmplt in conveyor['stock'] if re.search(tmplt, container_name)), None):
                            scs = tools.ConveyorSettingsContainer(settings, corporation, container)
                            settings.containers_stocks.append(scs)
                            stock_box = True
                    # if next((0 for tmplt in conveyor['blueprints'] if re.search(tmplt, container_name)), 1):
                    # получаем информацию по реакциям (если включены)
                    if settings.conveyor_with_reactions:
                        if next((1 for tmplt in conveyor['reactions']['formulas'] if re.search(tmplt, container_name)), None):
                            scs = tools.ConveyorSettingsContainer(settings, corporation, container)
                            settings.containers_react_formulas.append(scs)
                            formulas_box = True
                            if conveyor['reactions'].get('same_stock_container', False):
                                scs = tools.ConveyorSettingsContainer(settings, corporation, container)
                                settings.containers_stocks.append(scs)
                                stock_box = True
                        if not conveyor['reactions'].get('same_stock_container', False):
                            if 'stock' in conveyor['reactions']:
                                if next((1 for tmplt in conveyor['reactions']['stock'] if re.search(tmplt, container_name)), None):
                                    scs = tools.ConveyorSettingsContainer(settings, corporation, container)
                                    settings.containers_stocks.append(scs)
                                    stock_box = True
                    # получаем информацию по коробкам, куда можно направлять выход готовой продукции
                    if conveyor.get('output'):
                        if next((1 for tmplt in conveyor['output'] if re.search(tmplt, container_name)), None):
                            scs = tools.ConveyorSettingsContainer(settings, corporation, container)
                            settings.containers_output.append(scs)
                            output_box = True
                    # проверяем контейнеры, которые являются исключениями из списка, где роется конвейер
                    # (по остаточному принципу)
                    if not source_box and not stock_box and not formulas_box and not output_box:
                        if conveyor.get('exclude_hangars') and int(container_hangar[-1:]) in conveyor['exclude_hangars']:
                            exclude_box = True
                        if conveyor.get('exclude'):
                            if next((1 for tmplt in conveyor['exclude'] if re.search(tmplt, container_name)), None):
                                exclude_box = True
                        if exclude_box:
                            scs = tools.ConveyorSettingsContainer(settings, corporation, container)
                            settings.containers_exclude.append(scs)
                        else:
                            # получаем информацию по коробкам, откуда можно брать дополнительные чертежи (например T1)
                            if db.QSwaggerActivityCode.MANUFACTURING in settings.activities:
                                scb = tools.ConveyorSettingsContainer(settings, corporation, container)
                                settings.containers_additional_blueprints.append(scb)
                # если в этой корпорации не найдены основные параметры (контейнеры по названиям, то пропускаем корпу)
                if not settings.containers_sources:
                    del settings
                    continue
                # уточняем настройки поведения конвейера (секция behavior)
                if 'behavior' in conveyor:
                    behavior_market = conveyor['behavior'].get('market')
                    if behavior_market:
                        # пропускаем некорректные настройки (просто правильность синтаксиса настроек)
                        trade_corporation_names: typing.List[str] = behavior_market.get('corporations', [])
                        # поиск корпорации, которая торгует (видимо в Jita? но это не обязательно)
                        for trade_corporation_name in trade_corporation_names:
                            trade_corporation: db.QSwaggerCorporation = qid.get_corporation_by_name(trade_corporation_name)
                            if trade_corporation is None: continue
                            settings.trade_corporations.append(trade_corporation)
                            for container_id in trade_corporation.container_ids:
                                container: db.QSwaggerCorporationAssetsItem = trade_corporation.assets.get(container_id)
                                if not container:
                                    continue
                                container_name: str = container.name
                                if not container_name:
                                    continue
                                container_hangar: str = container.location_flag
                                if container_hangar[:-1] != 'CorpSAG':
                                    continue
                                # получаем информацию по коробкам где находится сток (оверсток) торговой корпы
                                if 1 == next((1 for tmplt in behavior_market['exclude_overstock'] if re.search(tmplt, container_name)), None):
                                    cssc = tools.ConveyorSettingsSaleContainer(settings, trade_corporation, container)
                                    settings.containers_sale_stocks.append(cssc)
                    # параметры поведения конвейера (расчёт копирки)
                    behavior_requirements = conveyor['behavior'].get('requirements')
                    if behavior_requirements:
                        settings.calculate_requirements = behavior_requirements.get('calculate', False)
                        settings.requirements_sold_threshold = behavior_requirements.get('sold_threshold', 0.2)
                # сохраняем полученные настройки, обрабатывать будем потом
                settings_of_conveyors.append(settings)

    if argv_prms['verbose_mode']:
        # вывод на экран того, что получилось
        for (idx, __s) in enumerate(settings_of_router):
            s: tools.RouterSettings = __s
            station: db.QSwaggerStation = qid.get_station_by_name(s.station)
            if idx > 0:
                print()
            print(f'{station.station_name}: #{station.station_id} [{station.station_type.name}] ({s.desc})')
            for p in s.output:
                product: typing.Optional[db.QSwaggerTypeId] = qid.get_type_id(p)
                print(f'  {product.type_id} {product.name}')
        print()

    if argv_prms['verbose_mode']:
        # вывод на экран того, что получилось
        for (idx0, __s) in enumerate(settings_of_conveyors):
            s: tools.ConveyorSettings = __s
            corporation: db.QSwaggerCorporation = s.corporation
            if idx0 > 0:
                print()
            print('industry corp: ', corporation.corporation_name)
            print('activities:    ', ','.join([str(_) for _ in s.activities]))
            stations: typing.List[int] = list(set([x.station_id for x in s.containers_sources] +
                                                  [x.station_id for x in s.containers_stocks] +
                                                  [x.station_id for x in s.containers_output] +
                                                  [x.station_id for x in s.containers_additional_blueprints] +
                                                  [x.station_id for x in s.containers_sale_stocks]))
            stations: typing.List[int] = sorted(stations, key=lambda x: qid.get_station(x).station_name if x else '')
            for station_id in stations:
                print(' station:      ', station_id, qid.get_station(station_id).station_name if station_id else None)
                z = sorted([x for x in s.containers_sources if x.station_id == station_id], key=lambda x: x.container_name)
                if z:
                    print('   source:     ', '\n                '.join([f'{x.container_id}   {x.container_name}' for x in z]))
                z = sorted([x for x in s.containers_stocks if x.station_id == station_id], key=lambda x: x.container_name)
                if z:
                    print('   stock:      ', '\n                '.join([f'{x.container_id}   {x.container_name}' for x in z]))
                z = sorted([x for x in s.containers_output if x.station_id == station_id], key=lambda x: x.container_name)
                if z:
                    print('   output:     ', '\n                '.join([f'{x.container_id}   {x.container_name}' for x in z]))
                if db.QSwaggerActivityCode.MANUFACTURING in s.activities:
                    z = sorted([x for x in s.containers_additional_blueprints if x.station_id == station_id], key=lambda x: x.container_name)
                    if z:
                        print('   blueprints: ', '\n                '.join([f'{x.container_id}   {x.container_name}' for x in z]))
                if s.conveyor_with_reactions:
                    z = sorted([x for x in s.containers_react_formulas if x.station_id == station_id], key=lambda x: x.container_name)
                    if z:
                        print('   formulas:   ', '\n                '.join([f'{x.container_id}   {x.container_name}' for x in z]))
                z = sorted([x for x in s.containers_sale_stocks if x.station_id == station_id], key=lambda x: x.container_name)
                if z:
                    print('   trader corp:', '\n                '.join([f'{x.trade_corporation.corporation_id} {x.trade_corporation.corporation_name}' for x in z]))
                    print('   sale stock: ', '\n                '.join([f'{x.container_id}   {x.container_name}' for x in z]))
            if s.fixed_number_of_runs is not None:
                print('fixed runs:    ', s.fixed_number_of_runs)

    # учитываем загруженные настройки и каталогизируем ассеты, чертежи и прочее всоответствии с ними
    for __s in settings_of_conveyors:
        s: tools.ConveyorSettings = __s
        s.recalc_container_locations()

    # вывод в отчёт результатов работы роутера
    render_html_conveyor_db.dump_router2_into_report(
        # путь, где будет сохранён отчёт
        argv_prms["workspace_cache_files_dir"],
        # данные (справочники)
        qid,
        # настройки генерации отчёта
        settings_of_router,
        settings_of_conveyors
    )
    # ---
    del qid

    # Вывод в лог уведомления, что всё завершилось (для отслеживания с помощью tail)
    print("\nConveyor v{}-db done".format(__version__))


if __name__ == "__main__":
    main()
