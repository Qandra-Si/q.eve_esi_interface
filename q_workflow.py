﻿""" Q.Workflow (desktop/mobile)

Prerequisites:
    * Have a Python 3 environment available to you (possibly by using a
      virtual environment: https://virtualenv.pypa.io/en/stable/).
    * Run pip install -r requirements.txt with this directory as your root.

    * Copy q_industrialist_settings.py.template into q_industrialist_settings.py and
      mood for your needs.
    * Create an SSO application at developers.eveonline.com with the scopes
      from g_client_scope list declared in q_industrialist_settings.py and the
      callback URL "https://localhost/callback/".
      Note: never use localhost as a callback in released applications.

To run this example, make sure you have completed the prerequisites and then
run the following command from this directory as the root:

>>> python eve_sde_tools.py
>>> python q_workflow.py --pilot="Qandra Si" --online --cache_dir=~/.q_industrialist

Requires application scopes:
    * esi-assets.read_corporation_assets.v1 - Requires role(s): Director
"""
import sys
import json
import requests

import eve_esi_interface as esi
import postgresql_interface as db

import q_industrialist_settings
import eve_esi_tools
import eve_sde_tools
import console_app
import render_html_workflow

from __init__ import __version__


g_module_default_settings = {
    # either "station_id" or "station_name" is required
    # if "station_id" is unknown, then the names of stations and structures will be
    # additionally loaded (too slow, please identify and set "station_id")
    "factory:station_id": 60003760,
    "factory:station_name": "Jita IV - Moon 4 - Caldari Navy Assembly Plant",
    # hangar, which stores blueprint copies to build T2 modules
    "factory:blueprints_hangars": [1]
}


def __get_blueprints_containers_with_data_loading(
        # esi input & output
        esi_interface,
        # настройки
        module_settings,
        # sde данные, загруженные из .converted_xxx.json файлов
        sde_type_ids,
        corp_assets_data):
    # esi input
    interface = esi_interface["interface"]
    corporation_id = esi_interface["corporation_id"]
    corporation_name = esi_interface["corporation_name"]
    # esi output
    esi_interface["corp_ass_names_data"] = []
    esi_interface["foreign_structures_data"] = {}

    # input setings
    hangars_filter = module_settings["factory:blueprints_hangars"]
    # output factory containers
    factory_containers = {
        "station_id": module_settings["factory:station_id"] if "factory:station_id" in module_settings else None,
        "station_name": module_settings["factory:station_name"] if "factory:station_name" in module_settings else None,
        "station_foreign": None,
        "containers": None
    }

    # пытаемся определить недостающее звено, либо station_id, либо station_name (если неизвестны)
    if not (factory_containers["station_id"] is None):
        station_id = factory_containers["station_id"]
        station_name = None
        factory_containers["station_foreign"] = next((a for a in corp_assets_data if a["item_id"] == int(station_id)), None) is None

        # поиск контейнеров на станции station_id в ангарах hangars_filter
        factory_containers["containers"] = eve_esi_tools.find_containers_in_hangars(
            station_id,
            hangars_filter,
            sde_type_ids,
            corp_assets_data)

        esi_interface["corp_ass_names_data"] = []
        corp_ass_named_ids = [bc["id"] for bc in factory_containers["containers"]]
        if not factory_containers["station_foreign"]:
            corp_ass_named_ids.append(station_id)
            station_name = next((an for an in esi_interface["corp_ass_names_data"] if an["item_id"] == station_id), None)

        if len(corp_ass_named_ids) > 0:
            # Requires role(s): Director
            esi_interface["corp_ass_names_data"] = interface.get_esi_data(
                "corporations/{}/assets/names/".format(corporation_id),
                json.dumps(corp_ass_named_ids, indent=0, sort_keys=False))
        print("\n'{}' corporation has {} custom asset's names".format(corporation_name, len(esi_interface["corp_ass_names_data"])))
        sys.stdout.flush()

        if factory_containers["station_foreign"]:
            # поиск одной единственной станции, которая не принадлежат корпорации (на них имеется офис,
            # но самой станции в ассетах нет)
            esi_interface["foreign_structures_data"] = {}
            foreign_structures_ids = [station_id]
            foreign_structures_forbidden_ids = []
            if len(foreign_structures_ids) > 0:
                # Requires: access token
                for structure_id in foreign_structures_ids:
                    try:
                        universe_structure_data = interface.get_esi_data(
                            "universe/structures/{}/".format(structure_id))
                        esi_interface["foreign_structures_data"].update({str(structure_id): universe_structure_data})
                    except requests.exceptions.HTTPError as err:
                        status_code = err.response.status_code
                        if status_code == 403:  # это нормально, что часть структур со временем могут оказаться Forbidden
                            foreign_structures_forbidden_ids.append(structure_id)
                        else:
                            raise
                    except:
                        print(sys.exc_info())
                        raise
            print("\n'{}' corporation has offices in {} foreign stations".format(corporation_name, len(esi_interface["foreign_structures_data"])))
            if len(foreign_structures_forbidden_ids) > 0:
                print("\n'{}' corporation has offices in {} forbidden stations : {}".format(corporation_name, len(foreign_structures_forbidden_ids), foreign_structures_forbidden_ids))
            sys.stdout.flush()

            if str(station_id) in esi_interface["foreign_structures_data"]:
                station_name = esi_interface["foreign_structures_data"][str(station_id)]["name"]

        # вывод на экран найденных station_id и station_name
        if station_name is None:
            raise Exception('Not found station name for factory {}!!!'.format(station_id))

    elif not (factory_containers["station_name"] is None):
        station_name = factory_containers["station_name"]

        esi_interface["corp_ass_names_data"] = []
        corp_ass_named_ids = eve_esi_tools.get_assets_named_ids(corp_assets_data)
        if len(corp_ass_named_ids) > 0:
            # Requires role(s): Director
            esi_interface["corp_ass_names_data"] = interface.get_esi_data(
                "corporations/{}/assets/names/".format(corporation_id),
                json.dumps(corp_ass_named_ids, indent=0, sort_keys=False))
        print("\n'{}' corporation has {} custom asset's names".format(corporation_name, len(esi_interface["corp_ass_names_data"])))
        sys.stdout.flush()

        station_id = next((an for an in esi_interface["corp_ass_names_data"] if an["name"] == station_name), None)
        factory_containers["station_foreign"] = station_id is None

        if factory_containers["station_foreign"]:
            # поиск тех станций, которые не принадлежат корпорации (на них имеется офис, но самой станции в ассетах нет)
            esi_interface["foreign_structures_data"] = {}
            foreign_structures_ids = eve_esi_tools.get_foreign_structures_ids(corp_assets_data)
            foreign_structures_forbidden_ids = []
            if len(foreign_structures_ids) > 0:
                # Requires: access token
                for structure_id in foreign_structures_ids:
                    try:
                        universe_structure_data = interface.get_esi_data(
                            "universe/structures/{}/".format(structure_id))
                        esi_interface["foreign_structures_data"].update({str(structure_id): universe_structure_data})
                    except requests.exceptions.HTTPError as err:
                        status_code = err.response.status_code
                        if status_code == 403:  # это нормально, что часть структур со временем могут оказаться Forbidden
                            foreign_structures_forbidden_ids.append(structure_id)
                        else:
                            raise
                    except:
                        print(sys.exc_info())
                        raise
            print("\n'{}' corporation has offices in {} foreign stations".format(corporation_name, len(esi_interface["foreign_structures_data"])))
            if len(foreign_structures_forbidden_ids) > 0:
                print("\n'{}' corporation has offices in {} forbidden stations : {}".format(corporation_name, len(foreign_structures_forbidden_ids), foreign_structures_forbidden_ids))
            sys.stdout.flush()

            __foreign_keys = esi_interface["foreign_structures_data"].keys()
            for __foreign_id in __foreign_keys:
                __foreign_dict = esi_interface["foreign_structures_data"][str(__foreign_id)]
                if __foreign_dict["name"] == station_name:
                    station_id = int(__foreign_id)
                    break

        # вывод на экран найденных station_id и station_name
        if station_id is None:
            raise Exception('Not found station identity for factory {}!!!'.format(station_name))

        # поиск контейнеров на станции station_id в ангарах hangars_filter
        factory_containers["containers"] = eve_esi_tools.find_containers_in_hangars(
            station_id,
            hangars_filter,
            sde_type_ids,
            corp_assets_data)

    else:
        raise Exception('Not found station identity and name!!!')

    factory_containers["station_id"] = station_id
    factory_containers["station_name"] = station_name

    # получение названий контейнеров и сохранение из в списке контейнеров
    for __cont_dict in factory_containers["containers"]:
        __item_id = __cont_dict["id"]
        __item_name = next((an for an in esi_interface["corp_ass_names_data"] if an["item_id"] == __item_id), None)
        if not (__item_name is None):
            __cont_dict["name"] = __item_name["name"]

    return factory_containers


def __get_monthly_manufacturing_scheduler(
        # настройки
        scheduler_job_settings,
        # sde данные, загруженные из .converted_xxx.json файлов
        sde_type_ids,
        sde_named_type_ids,
        sde_bp_materials,
        sde_market_groups,
        # esi данные, загруженные с серверов CCP
        corp_blueprints_data,
        corp_industry_jobs_data,
        # данные, полученные в результате анализа и перекомпоновки входных списков
        factory_containers):
    # конвертация ETF в список item-ов
    scheduler = {
        "monthly_jobs": [],
        "scheduled_blueprints": [],
        "factory_containers": factory_containers,
        "factory_repository": [],
        "factory_blueprints": [],
        "missing_blueprints": [],
        "overplus_blueprints": [],
    }
    scheduled_blueprints = scheduler["scheduled_blueprints"]
    factory_blueprints = scheduler["factory_blueprints"]
    missing_blueprints = scheduler["missing_blueprints"]
    overplus_blueprints = scheduler["overplus_blueprints"]

    def push_into_scheduled_blueprints(type_id, quantity, name, product_type_id):
        __sbd227 = next((sb for sb in scheduled_blueprints if sb["type_id"] == type_id), None)
        if __sbd227 is None:
            __sbd227 = {"type_id": type_id,
                        "name": eve_sde_tools.get_item_name_by_type_id(sde_type_ids, type_id),
                        "product": {"scheduled_quantity": int(quantity), "name": name, "type_id": product_type_id}}
            # получаем данные по чертежу, - продукция, кол-во производимой продукции, материалы
            __ptid227, __pq227, __pm227 = \
                eve_sde_tools.get_manufacturing_product_by_blueprint_type_id(type_id, sde_bp_materials)
            if not (__ptid227 is None):
                if __ptid227 != product_type_id:
                    raise Exception('Unable to match product {} and blueprint()!!!'.format(product_type_id, type_id))
                __sbd227["products_per_run"] = __pq227
                __sbd227["manufacturing"] = {"materials": __pm227}
            scheduled_blueprints.append(__sbd227)
        else:
            __sbd227["product"]["scheduled_quantity"] += int(quantity)

    def push_into_factory_blueprints(type_id, runs):
        __fbd235 = next((fb for fb in factory_blueprints if fb["type_id"] == type_id), None)
        if __fbd235 is None:
            __fbd235 = {"type_id": type_id,
                        "runs": int(runs),
                        "quantity": 1,
                        # "name": name,
                        # "meta_group": meta_group
                        }
            factory_blueprints.append(__fbd235)
        else:
            __fbd235["runs"] += int(runs)
            __fbd235["quantity"] += 1

    # конвертация ETF в список item-ов
    for ship in scheduler_job_settings:
        __eft = ship["eft"]
        __total_quantity = ship["quantity"]
        __converted = eve_sde_tools.get_items_list_from_eft(__eft, sde_named_type_ids)
        __converted.update({"quantity": __total_quantity})
        if not (__converted["ship"] is None):
            __blueprint_type_id, __blueprint_dict = eve_sde_tools.get_blueprint_type_id_by_product_id(
                __converted["ship"]["type_id"],
                sde_bp_materials
            )
            __converted["ship"].update({"blueprint": {
                "type_id": __blueprint_type_id,
                # "manufacturing": __blueprint_dict["activities"]["manufacturing"]
            }})
        __converted["items"].sort(key=lambda i: i["name"])
        for __item_dict in __converted["items"]:
            __item_type_id = __item_dict["type_id"]
            __blueprint_type_id, __blueprint_dict = eve_sde_tools.get_blueprint_type_id_by_product_id(
                __item_type_id,
                sde_bp_materials
            )
            if not (__blueprint_type_id is None) and ("manufacturing" in __blueprint_dict["activities"]):
                __item_dict.update({"blueprint": {
                    "type_id": __blueprint_type_id,
                    # "manufacturing": __blueprint_dict["activities"]["manufacturing"]
                }})
        scheduler["monthly_jobs"].append(__converted)

    # формирование списка чертежей, которые необходимы для постройки запланированного кол-ва фитов
    for job in scheduler["monthly_jobs"]:
        __ship = job["ship"]
        __total_quantity = job["quantity"]
        __items = job["items"]
        # добавляем в список БПЦ чертёж хула корабля (это может быть и БПО в итоге...)
        if not (__ship is None):
            if "blueprint" in __ship:
                push_into_scheduled_blueprints(
                    __ship["blueprint"]["type_id"],
                    __total_quantity,
                    __ship["name"],
                    __ship["type_id"]
                )
        # подсчитываем количество БПЦ, необходимых для постройки T2-модулей этого фита
        __bpc_for_fit = [{"id": i["blueprint"]["type_id"],
                          "q": __total_quantity * i["quantity"],
                          "nm": i["name"],
                          "prod": i["type_id"]}
                         for i in __items if
                         ("blueprint" in i) and
                         ("metaGroupID" in i["details"]) and
                         (i["details"]["metaGroupID"] == 2)]
        for bpc in __bpc_for_fit:
            push_into_scheduled_blueprints(
                bpc["id"],
                bpc["q"],
                bpc["nm"],
                bpc["prod"]
            )

    # формирование списка чертежей имеющихся на станции в указанных контейнерах
    factory_container_ids = [fc["id"] for fc in factory_containers["containers"]]
    # A range of numbers with a minimum of -2 and no maximum value where -1 is an original and -2 is a copy.
    # It can be a positive integer if it is a stack of blueprint originals fresh from the market (e.g. no
    # activities performed on them yet).
    scheduler["factory_repository"] = [bp for bp in corp_blueprints_data if
                                       (bp["location_id"] in factory_container_ids) and
                                       (bp["quantity"] == -2)]

    # формирование сводного списка чертежей фабрики, с суммарным кол-вом run-ов
    factory_repository = scheduler["factory_repository"]
    for bp in factory_repository:
        __blueprint_type_id = bp["type_id"]
        push_into_factory_blueprints(__blueprint_type_id, bp["runs"])
    # получение названий чертежей и сохранение их в сводном списке чертежей фабрики
    for bp in factory_blueprints:
        __blueprint_type_id = bp["type_id"]
        __product_type_id, __dummy0, __dummy1 = \
            eve_sde_tools.get_manufacturing_product_by_blueprint_type_id(__blueprint_type_id, sde_bp_materials)
        bp["name"] = eve_sde_tools.get_item_name_by_type_id(sde_type_ids, __blueprint_type_id)
        bp["product_type_id"] = __product_type_id
        # на станции может быть куча всяких БПЦ, нас будут интересовать только Т2 БПЦ
        if not (str(__blueprint_type_id) in sde_type_ids):
            continue
        __item_dict = sde_type_ids[str(__blueprint_type_id)]
        bp["meta_group"] = int(__item_dict["metaGroupID"]) if "metaGroupID" in __item_dict else None

    # расчёт кол-ва run-ов с учётом кратности run-ов T2-чертежей (в списке scheduled_blueprints)
    for __sb_dict in scheduled_blueprints:
        __blueprint_type_id = __sb_dict["type_id"]
        __scheduled_products = __sb_dict["product"]["scheduled_quantity"]
        __product_type_id = __sb_dict["product"]["type_id"]
        __products_per_run = __sb_dict["products_per_run"]
        # получаем список market-груп, которым принадлежит продукт
        __market_groups_chain = eve_sde_tools.get_market_groups_chain_by_type_id(
            sde_type_ids,
            sde_market_groups,
            __product_type_id)
        __market_groups = set(__market_groups_chain)
        # в расчётах учитывается правило: Т2 модули - 10 ранов, все хулы - 4 рана, все риги - 3 рана
        __blueprint_copy_runs = 1
        if bool(__market_groups & {9, 157, 11}):  # Ship Equipment, Drones, Ammunition & Charges
            __blueprint_copy_runs = 10
        elif 4 in __market_groups:  # Ships
            __blueprint_copy_runs = 4
        elif 955 in __market_groups:  # Ship and Module Modifications
            __blueprint_copy_runs = 3
        __single_run_quantity = __blueprint_copy_runs * __products_per_run
        __scheduled_blueprints_quantity = \
            int(__scheduled_products + __single_run_quantity - 1) // int(__single_run_quantity)
        # сохраняем кол-во БПЦ по правилу выше
        # внимание! на самом деле это магическое число зависит от точных знаний - сколько прогонов
        # может быть у чертежа? но это "рекомендуемое" число, и вовсе не факт, что так и будет...
        __sb_dict["blueprints_quantity"] = __scheduled_blueprints_quantity
        # тот самый "магический" множитель - кол-во прогонов на чертёж (ожидаемое)
        __sb_dict["blueprint_copy_runs"] = __blueprint_copy_runs

    # формирование списка недостающих чертежей
    for __sb_dict in scheduled_blueprints:
        # получаем данные по чертежу, запланированному к использованию
        __blueprint_type_id = __sb_dict["type_id"]
        __product_type_id = __sb_dict["product"]["type_id"]
        __required_blueprints = __sb_dict["blueprints_quantity"]
        __scheduled_products = __sb_dict["product"]["scheduled_quantity"]
        __products_per_run = __sb_dict["products_per_run"]
        __blueprint_copy_runs = __sb_dict["blueprint_copy_runs"]
        __single_run_quantity = __blueprint_copy_runs * __products_per_run
        # получаем данные по имеющимся чертежам
        __exist = [fb for fb in factory_blueprints if fb["type_id"] == __blueprint_type_id]
        # если чертежей и вовсе нет, то сразу создаём запись о недостающем количестве
        if not __exist:
            missing_blueprints.append({
                "type_id": __blueprint_type_id,
                "name": __sb_dict["name"],
                "product_type_id": __product_type_id,
                "required_quantity": __required_blueprints,
                "there_are_no_blueprints": True,  # признак того, что нет ни одного чертежа этого типа
            })
        else:
            # суммируем прогоны чертежей и переводим их в количество продуктов, которые м.б. построено
            __exist_runs = sum([fb["runs"] for fb in __exist])
            __exist_run_products = __exist_runs * __products_per_run
            # если чертежей недостаточно, то расчитываем недостающее кол-во чертежей
            if __exist_run_products < __scheduled_products:
                __required_run_products = __scheduled_products - __exist_run_products
                __required_blueprints = \
                    int(__required_run_products + __single_run_quantity - 1) // int(__single_run_quantity)
                missing_blueprints.append({
                    "type_id": __blueprint_type_id,
                    "name": __sb_dict["name"],
                    "product_type_id": __product_type_id,
                    "required_quantity": __required_blueprints,
                })
            # если чертежей избыточное количество, то расчитываем кол-во лишних
            elif __exist_run_products > __scheduled_products:
                __unnecessary_run_products = __exist_run_products - __scheduled_products
                __unnecessary_blueprints = \
                    int(__unnecessary_run_products) // int(__single_run_quantity)
                # возможна ситуация: имеется чертежей на 70 продуктов, требуется 65 продуктов,
                # но каждый ран - 10 продуктов, таким образом (70-65)//10 - все чертежи нужны
                if __unnecessary_blueprints > 0:
                    overplus_blueprints.append({
                        "type_id": __blueprint_type_id,
                        "name": __sb_dict["name"],
                        "product_type_id": __product_type_id,
                        "unnecessary_quantity": __unnecessary_blueprints,
                    })

    # формирование списка избыточных чертежей
    scheduled_blueprint_type_ids = [int(sb["type_id"]) for sb in scheduled_blueprints]
    for __fb_dict in factory_blueprints:
        __blueprint_type_id = __fb_dict["type_id"]
        __meta_group = __fb_dict["meta_group"]
        __product_type_id = __fb_dict["product_type_id"]
        # на станции может быть куча всяких БПЦ, нам интересуют излишки только Т2 чертежей
        if __meta_group is None:
            continue
        elif int(__meta_group) != 2:
            continue
        # если БПЦ с указанным типом вовсе отсутствует в списке требуемых для постройки, то сразу
        # создаём запись об излишках, где все чертежи этого типа будут лишними
        if not (__blueprint_type_id in scheduled_blueprint_type_ids):
            overplus_blueprints.append({
                "type_id": __blueprint_type_id,
                "name": __fb_dict["name"],
                "product_type_id": __product_type_id,
                "unnecessary_quantity": __fb_dict["quantity"],
                "all_of_them": True  # признак, что все чертежи этого типа - лишние
            })

    return scheduler


def main():
    qidb = db.QIndustrialistDatabase("workflow", debug=True)
    qidb.connect(q_industrialist_settings.g_database)
    module_settings = qidb.load_module_settings(g_module_default_settings)
    db_monthly_jobs = qidb.select_all_rows(
        "SELECT wmj_id,wmj_active,wmj_quantity,wmj_eft,wmj_remarks "
        "FROM workflow_monthly_jobs;")
    db_factory_containers = qidb.select_all_rows(
        "SELECT wfc_id,wfc_name "
        "FROM workflow_factory_containers;")
    del qidb

    db_monthly_jobs = [{"eft": wmj[3], "quantity": wmj[2]} for wmj in db_monthly_jobs]
    db_factory_containers = [{"id": wfc[0], "name": wfc[1]} for wfc in db_factory_containers]

    # работа с параметрами командной строки, получение настроек запуска программы, как то: работа в offline-режиме,
    # имя пилота ранее зарегистрированного и для которого имеется аутентификационный токен, регистрация нового и т.д.
    argv_prms = console_app.get_argv_prms()

    # настройка Eve Online ESI Swagger interface
    auth = esi.EveESIAuth(
        '{}/auth_cache'.format(argv_prms["workspace_cache_files_dir"]),
        debug=True)
    client = esi.EveESIClient(
        auth,
        debug=False,
        logger=True,
        user_agent='Q.Industrialist v{ver}'.format(ver=__version__))
    interface = esi.EveOnlineInterface(
        client,
        q_industrialist_settings.g_client_scope,
        cache_dir='{}/esi_cache'.format(argv_prms["workspace_cache_files_dir"]),
        offline_mode=argv_prms["offline_mode"])

    authz = interface.authenticate(argv_prms["character_names"][0])
    character_id = authz["character_id"]
    character_name = authz["character_name"]

    sde_type_ids = eve_sde_tools.read_converted(argv_prms["workspace_cache_files_dir"], "typeIDs")
    sde_bp_materials = eve_sde_tools.read_converted(argv_prms["workspace_cache_files_dir"], "blueprints")
    sde_market_groups = eve_sde_tools.read_converted(argv_prms["workspace_cache_files_dir"], "marketGroups")

    sde_named_type_ids = eve_sde_tools.convert_sde_type_ids(sde_type_ids)

    # Public information about a character
    character_data = interface.get_esi_data(
        "characters/{}/".format(character_id))
    # Public information about a corporation
    corporation_data = interface.get_esi_data(
        "corporations/{}/".format(character_data["corporation_id"]))

    corporation_id = character_data["corporation_id"]
    corporation_name = corporation_data["name"]
    print("\n{} is from '{}' corporation".format(character_name, corporation_name))
    sys.stdout.flush()

    # для того, чтобы получить названия коробок и в каком ангаре они расположены, надо загрузить
    # данные по ассетам, т.к. только в этих данных можно учитывая иерархию пересчитать коробки
    # в нужном ангаре

    # Requires role(s): Director
    corp_assets_data = interface.get_esi_paged_data(
        "corporations/{}/assets/".format(corporation_id))
    print("\n'{}' corporation has {} assets".format(corporation_name, len(corp_assets_data)))
    sys.stdout.flush()

    esi_interface = {
        "interface": interface,
        "corporation_id": corporation_id,
        "corporation_name": corporation_name,
        "corp_ass_names_data": None,
        "foreign_structures_data": None
    }
    factory_containers = __get_blueprints_containers_with_data_loading(
        esi_interface,
        module_settings,
        sde_type_ids,
        corp_assets_data
    )
    # обновление данных в БД (названия контейнеров, и первичное автозаполнение)
    if len(db_factory_containers) == 0:
        # "containers": [
        #    {"id": 1032456650838,
        #     "type_id": 33011,
        #     "name": "t2 fit 2"},... ]
        qidb = db.QIndustrialistDatabase("workflow", debug=True)
        qidb.connect(q_industrialist_settings.g_database)
        for fc in factory_containers["containers"]:
            qidb.execute(
                "INSERT INTO workflow_factory_containers(wfc_id,wfc_name) VALUES(%s,%s);",
                fc["id"], fc["name"])
        del qidb

    print('\nFound factory station {} with containers in hangars...'.format(factory_containers["station_name"]))
    print('  {} = {}'.format(factory_containers["station_id"], factory_containers["station_name"]))
    print('  blueprint hangars = {}'.format(module_settings["factory:blueprints_hangars"]))
    print('  blueprint containers = {}'.format(len([fc["id"] for fc in factory_containers["containers"]])))
    sys.stdout.flush()

    # Requires role(s): Director
    corp_blueprints_data = interface.get_esi_paged_data(
        "corporations/{}/blueprints/".format(corporation_id))
    print("\n'{}' corporation has {} blueprints".format(corporation_name, len(corp_blueprints_data)))
    sys.stdout.flush()

    # Requires role(s): Factory_Manager
    corp_industry_jobs_data = interface.get_esi_paged_data(
        "corporations/{}/industry/jobs/".format(corporation_id))
    print("\n'{}' corporation has {} industry jobs".format(corporation_name, len(corp_industry_jobs_data)))
    sys.stdout.flush()

    # формирование набора данных для построения отчёта
    corp_manufacturing_scheduler = __get_monthly_manufacturing_scheduler(
        # данные, полученные из БД
        db_monthly_jobs,
        # sde данные, загруженные из .converted_xxx.json файлов
        sde_type_ids,
        sde_named_type_ids,
        sde_bp_materials,
        sde_market_groups,
        # esi данные, загруженные с серверов CCP
        corp_blueprints_data,
        corp_industry_jobs_data,
        # данные, полученные в результате анализа и перекомпоновки входных списков
        factory_containers
    )
    eve_esi_tools.dump_debug_into_file(argv_prms["workspace_cache_files_dir"], "corp_manufacturing_scheduler", corp_manufacturing_scheduler)

    print('\nFound {} EFT fits in settings...'.format(len(factory_containers)))
    print('  scheduled blueprints = {}'.format(len(corp_manufacturing_scheduler["scheduled_blueprints"])))
    print('  factory repository = {}'.format(len(corp_manufacturing_scheduler["factory_repository"])))
    print('  factory blueprints = {}'.format(len(corp_manufacturing_scheduler["factory_blueprints"])))
    sys.stdout.flush()

    print("\nBuilding report...")
    sys.stdout.flush()

    render_html_workflow.dump_workflow_into_report(
        # путь, где будет сохранён отчёт
        argv_prms["workspace_cache_files_dir"],
        # sde данные, загруженные из .converted_xxx.json файлов
        sde_type_ids,
        sde_market_groups,
        # данные, полученные в результате анализа и перекомпоновки входных списков
        corp_manufacturing_scheduler
    )

    # Вывод в лог уведомления, что всё завершилось (для отслеживания с помощью tail)
    print("\nDone")


if __name__ == "__main__":
    main()
