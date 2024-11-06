﻿""" Q.Blueprints (desktop/mobile)

Prerequisites:
    * Have a Python 3 environment available to you (possibly by using a
      virtual environment: https://virtualenv.pypa.io/en/stable/).
    * Run pip install -r requirements.txt --user with this directory.
      or
      Run pip install -r requirements.txt with this directory as your root.

    * Copy q_industrialist_settings.py.template into q_industrialist_settings.py and
      mood for your needs.
    * Copy q_blueprints_settings.py.template into q_blueprints_settings.py and
      mood for your needs.
    * Create an SSO application at developers.eveonline.com with the scopes
      from g_client_scope list declared in q_industrialist_settings.py and the
      callback URL "https://localhost/callback/".
      Note: never use localhost as a callback in released applications.

To run this example, make sure you have completed the prerequisites and then
run the following command from this directory as the root:

$ chcp 65001 & @rem on Windows only!
$ python eve_sde_tools.py --cache_dir=~/.q_industrialist
$ python q_blueprints.py --pilot="Qandra Si" --pilot="Your Name" --online --cache_dir=~/.q_industrialist

Required application scopes:
    * esi-assets.read_corporation_assets.v1 - Requires role(s): Director
    * esi-corporations.read_blueprints.v1 - Requires role(s): Director
    * esi-industry.read_corporation_jobs.v1 - Requires role(s): Factory_Manager
    * esi-contracts.read_corporation_contracts.v1 - Requires: access token
"""
import sys

import requests

import eve_esi_interface as esi

import eve_esi_tools
import eve_sde_tools
import console_app
import q_industrialist_settings
import render_html_blueprints

from __init__ import __version__


def __push_location_into_blueprints_locations(
        __location_id,
        blueprints_locations,
        sde_inv_names,
        sde_inv_items,
        corp_assets_tree,
        corp_ass_names_data,
        foreign_structures_data):
    if not (str(__location_id) in blueprints_locations):
        __loc_dict = eve_esi_tools.get_universe_location_by_item(
            __location_id,
            sde_inv_names,
            sde_inv_items,
            corp_assets_tree,
            corp_ass_names_data,
            foreign_structures_data
        )
        if "station" in __loc_dict:
            blueprints_locations.update({str(__location_id): __loc_dict})


def __build_blueprints(
        corp_blueprints_data,
        corp_industry_jobs_data,
        eve_market_prices_data,
        corp_contracts_data,
        corp_contract_items_data,
        various_characters_data,
        sde_type_ids,
        sde_inv_names,
        sde_inv_items,
        sde_market_groups,
        corp_assets_tree,
        corp_ass_names_data,
        foreign_structures_data):
    blueprints = []
    blueprints_locations = {}
    keys_to_skip_on_compare = ['name', 'item_id', 'q', 'base_price', 'average_price', 'adjusted_price']
    for __blueprint_dict in corp_blueprints_data:
        # A range of numbers with a minimum of -2 and no maximum value where -1 is an original and -2 is a copy.
        # It can be a positive integer if it is a stack of blueprint originals fresh from the market (e.g. no
        # activities performed on them yet).
        __quantity: int = __blueprint_dict["quantity"]
        __is_blueprint_copy: bool = bool(__quantity == -2)
        __type_id: int = int(__blueprint_dict["type_id"])
        __type_desc = sde_type_ids.get(str(__type_id), None)
        if __type_desc is None:
            __type_desc = {}
            __is_t2_blueprint = None
        else:
            __is_t2_blueprint = __type_desc.get("metaGroupID", None) == 2
            # отсеиваем подраздел Manufacture & Research, который встречается в blueprints-данных от ССР, например:
            # будут пропущены Intact Power Cores, Malfunctioning Weapon Subroutines и т.п.
            # но поскольку проверка выполняется с помощью marketGroupID, то дополнительно проверяем, что чертёж
            # является T2, и соответственно поскольку не продаётся на рынке - всё равно должен попасть в отчёт
            if not __is_t2_blueprint:
                __group_id = eve_sde_tools.get_root_market_group_by_type_id(sde_type_ids, sde_market_groups, __type_id)
                if __group_id != 2:  # Blueprints & Reactions
                    continue
        __blueprint_id = __blueprint_dict["item_id"]
        __location_id = __blueprint_dict["location_id"]
        __blueprint = {
            "item_id": __blueprint_id,
            "type_id": __type_id,
            "name": __type_desc.get("name", {}).get("en", "Unknown Type {} Blueprint".format(__type_id)),
            "copy": __is_blueprint_copy,
            "me": __blueprint_dict["material_efficiency"],
            "te": __blueprint_dict["time_efficiency"],
            "q": 1 if __quantity < 0 else __quantity,
            "loc": __location_id,
            "flag": __blueprint_dict["location_flag"]
        }
        # если чертёж в единичном экземпляре, не stacked, смотрим что с ним происходит? (jobs?)
        blueprint_job_found = False
        if __quantity < 0:
            __job_dict = next((j for j in corp_industry_jobs_data if j['blueprint_id'] == int(__blueprint_id)), None)
            if not (__job_dict is None):
                blueprint_job_found = True
                # особенность : чертежи могут отсутствовать в assets по указанному location_id, при этом чертёж будет в
                # blueprints, но его location_id будет указывать на станцию, а не на контейнер, в то же время в
                # industrial jobs этот же самый чертёж будет находиться в списке и иметь blueprint_location_id который
                # указывает на искомый контейнер
                __location_id = __job_dict["blueprint_location_id"]
                # сохранение информации о текущей работе, ведущейся с использованием чертежа
                __blueprint.update({
                    "st": __job_dict["status"],
                    "act": __job_dict["activity_id"],
                    "loc": __location_id,  # переопределяем!!!
                    "out": __job_dict["output_location_id"],
                })
                # осуществляем поиск местоположения чертежа
                __push_location_into_blueprints_locations(
                    __job_dict["output_location_id"],
                    blueprints_locations,
                    sde_inv_names,
                    sde_inv_items,
                    corp_assets_tree,
                    corp_ass_names_data,
                    foreign_structures_data)
        # ищем уже существующий чертёж в списке ранее добавленных
        same_blueprint_found = None
        for b in blueprints:
            # не стравниваем чертежи у одного из которых не ведутся работы, иначе код ниже не сможет
            # сравнить просто перебирая ключи dict-ов с разным составом параметров
            if blueprint_job_found == bool(b.get('st') is None):
                continue
            same_blueprint = True
            for key in b:
                if key in keys_to_skip_on_compare:
                    continue
                elif not (key in __blueprint):
                    same_blueprint = False
                    break
                elif b[key] != __blueprint[key]:
                    same_blueprint = False
                    break
            if same_blueprint:
                same_blueprint_found = b
                break
        if not same_blueprint_found:
            # T2 чертежи не имеют какую-то точную маркет-цену, т.к. либо не продаются, либо продаются через
            # контракты, поэтому base_price и/или average_price, или adjusted_price невалидны
            if __is_t2_blueprint == False:
                # выясняем стоимость чертежа
                if "basePrice" in __type_desc:
                    __blueprint.update({"base_price": __type_desc["basePrice"]})
                else:
                    __price_dict = next((p for p in eve_market_prices_data if p['type_id'] == int(__type_id)), None)
                    if not (__price_dict is None):
                        if "average_price" in __price_dict:
                            __blueprint.update({"average_price": __price_dict["average_price"]})
                        elif "adjusted_price" in __price_dict:
                            __blueprint.update({"adjusted_price": __price_dict["adjusted_price"]})
            # осуществляем поиск местоположения чертежа
            __push_location_into_blueprints_locations(
                __location_id,
                blueprints_locations,
                sde_inv_names,
                sde_inv_items,
                corp_assets_tree,
                corp_ass_names_data,
                foreign_structures_data)
            # добавляем собранную информацию в список чертежей
            blueprints.append(__blueprint)
        else:
            same_blueprint_found["q"] += __blueprint["q"]

    # debug contracts only: blueprints = []
    # debug contracts only: blueprints_locations = {}

    # в рамках работы с чертежами, нас интересует только набор контрактов, в которых продаются чертежи
    # ищем публичные контракты типа "обмен предметами"
    for __contract_items_dict in corp_contract_items_data:
        __contract_id_key = __contract_items_dict.keys()
        for __contract_id in __contract_id_key:
            __items = __contract_items_dict[str(__contract_id)]
            for __items_dict in __items:
                # пропускаем отклонения от нормы, а также контракты на покупку, а не на продажу
                if not ("is_included" in __items_dict):
                   continue
                elif not bool(__items_dict["is_included"]):
                   continue
                __type_id = __items_dict["type_id"]
                __type_desc = sde_type_ids.get(str(__type_id), {})
                __is_t2_blueprint = __type_desc.get("metaGroupID", None) == 2
                # отсеиваем подраздел Manufacture & Research, который встречается в blueprints-данных от ССР, например:
                # будут пропущены Intact Power Cores, Malfunctioning Weapon Subroutines и т.п.
                # но поскольку проверка выполняется с помощью marketGroupID, то дополнительно проверяем, что чертёж
                # является T2, и соответственно поскольку не продаётся на рынке - всё равно должен попасть в отчёт
                if __is_t2_blueprint == False:
                    # Blueprints and Reactions (добавляем только этот тип), а также T2-чертежи
                    __group_id = eve_sde_tools.get_basis_market_group_by_type_id(sde_type_ids, sde_market_groups, __type_id)
                    if __group_id != 2:
                        continue
                # raw_quantity = -1 indicates that the item is a singleton (non-stackable). If the item happens to
                # be a Blueprint, -1 is an Original and -2 is a Blueprint Copy
                __is_blueprint_copy: bool = False
                if "raw_quantity" in __items_dict:
                    __raw_qauntity = __items_dict["raw_quantity"]
                    if __raw_qauntity == -2:
                        __is_blueprint_copy = True
                # получение данных по чертежу, находящемуся в продаже
                __quantity = __items_dict["quantity"]
                # получение общих данных данных по контракту
                __contract_dict = next((c for c in corp_contracts_data if c['contract_id'] == int(__contract_id)), None)
                __location_id = __contract_dict["start_location_id"]
                __issuer_id = __contract_dict["issuer_id"]
                __issuer_name = next((list(i.values())[0]["name"] for i in various_characters_data if int(list(i.keys())[0]) == int(__issuer_id)), None)
                __blueprint = {
                    "item_id": __items_dict["record_id"],
                    "type_id": __type_id,
                    "name": __type_desc.get("name", {}).get("en", "Unknown Type {} Blueprint".format(__type_id)),
                    "copy": __is_blueprint_copy,
                    # "me": None,
                    # "te": None,
                    "q": __quantity,
                    "loc": __location_id,
                    "flag": __contract_dict["title"],
                    "price": __contract_dict["price"],
                    "cntrct_sta": __contract_dict["status"],
                    "cntrct_typ": __contract_dict["type"],
                    "cntrct_issuer": __issuer_id,
                    "cntrct_issuer_name": __issuer_name
                }
                # осуществляем поиск местоположения чертежа
                __push_location_into_blueprints_locations(
                    __location_id,
                    blueprints_locations,
                    sde_inv_names,
                    sde_inv_items,
                    corp_assets_tree,
                    corp_ass_names_data,
                    foreign_structures_data)
                # добавляем собранную информацию в список чертежей
                blueprints.append(__blueprint)

    return blueprints, blueprints_locations


def main():
    # работа с параметрами командной строки, получение настроек запуска программы, как то: работа в offline-режиме,
    # имя пилота ранее зарегистрированного и для которого имеется аутентификационный токен, регистрация нового и т.д.
    argv_prms = console_app.get_argv_prms()

    sde_type_ids = eve_sde_tools.read_converted(argv_prms["workspace_cache_files_dir"], "typeIDs")
    sde_inv_names = eve_sde_tools.read_converted(argv_prms["workspace_cache_files_dir"], "invNames")
    sde_inv_items = eve_sde_tools.read_converted(argv_prms["workspace_cache_files_dir"], "invItems")
    sde_market_groups = eve_sde_tools.read_converted(argv_prms["workspace_cache_files_dir"], "marketGroups")

    corps_blueprints = {}
    eve_market_prices_data = None
    various_characters_data = []
    for pilot_name in argv_prms["character_names"]:
        # настройка Eve Online ESI Swagger interface
        auth = esi.EveESIAuth(
            '{}/auth_cache'.format(argv_prms["workspace_cache_files_dir"]),
            debug=True)
        client = esi.EveESIClient(
            auth,
            q_industrialist_settings.g_client_id,
            keep_alive=True,
            debug=argv_prms["verbose_mode"],
            logger=True,
            user_agent='Q.Industrialist v{ver}'.format(ver=__version__),
            restrict_tls13=q_industrialist_settings.g_client_restrict_tls13)
        interface = esi.EveOnlineInterface(
            client,
            q_industrialist_settings.g_client_scope,
            cache_dir='{}/esi_cache'.format(argv_prms["workspace_cache_files_dir"]),
            offline_mode=argv_prms["offline_mode"])

        authz = interface.authenticate(pilot_name)
        character_id = authz["character_id"]
        character_name = authz["character_name"]

        # Public information about a character
        character_data = interface.get_esi_data(
            "characters/{}/".format(character_id),
            fully_trust_cache=True)
        # Public information about a corporation
        corporation_data = interface.get_esi_data(
            "corporations/{}/".format(character_data["corporation_id"]),
            fully_trust_cache=True)

        corporation_id = character_data["corporation_id"]
        corporation_name = corporation_data["name"]
        print("\n{} is from '{}' corporation".format(character_name, corporation_name))
        sys.stdout.flush()

        various_characters_data.append({str(corporation_id): character_data})

        if eve_market_prices_data is None:
            try:
                # Public information about market prices
                eve_market_prices_data = interface.get_esi_paged_data("markets/prices/")
                print("\nEVE market has {} prices".format(len(eve_market_prices_data) if not (eve_market_prices_data is None) else 0))
                sys.stdout.flush()
            except requests.exceptions.HTTPError as err:
                status_code = err.response.status_code
                if status_code == 404:  # 2020.12.03 поломался доступ к ценам маркета (ССР-шники "внесли правки")
                    eve_market_prices_data = []
                else:
                    raise
            except:
                print(sys.exc_info())
                raise

        # Requires role(s): Director
        corp_assets_data = interface.get_esi_paged_data(
            "corporations/{}/assets/".format(corporation_id))
        print("\n'{}' corporation has {} assets".format(corporation_name, len(corp_assets_data)))
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

        # Получение названий контейнеров, станций, и т.п. - всё что переименовывается ingame
        corp_ass_named_ids = eve_esi_tools.get_assets_named_ids(corp_assets_data)
        # Requires role(s): Director
        corp_ass_names_data = interface.get_esi_piece_data(
            "corporations/{}/assets/names/".format(corporation_id),
            corp_ass_named_ids)
        print("\n'{}' corporation has {} custom asset's names".format(corporation_name, len(corp_ass_names_data)))
        sys.stdout.flush()
        del corp_ass_named_ids

        # Поиск тех станций, которые не принадлежат корпорации (на них имеется офис, но самой станции в ассетах нет)
        foreign_structures_data = {}
        foreign_structures_ids = eve_esi_tools.get_foreign_structures_ids(corp_assets_data)
        foreign_structures_forbidden_ids = []
        if len(foreign_structures_ids) > 0:
            # Requires: access token
            for structure_id in foreign_structures_ids:
                try:
                    universe_structure_data = interface.get_esi_data(
                        "universe/structures/{}/".format(structure_id),
                        fully_trust_cache=True)
                    foreign_structures_data.update({str(structure_id): universe_structure_data})
                except requests.exceptions.HTTPError as err:
                    status_code = err.response.status_code
                    if status_code == 403:  # это нормально, что часть структур со временем могут оказаться Forbidden
                        foreign_structures_forbidden_ids.append(structure_id)
                    else:
                        raise
                except:
                    print(sys.exc_info())
                    raise
        print("\n'{}' corporation has offices in {} foreign stations".format(corporation_name, len(foreign_structures_data)))
        if len(foreign_structures_forbidden_ids) > 0:
            print("\n'{}' corporation has offices in {} forbidden stations : {}".format(corporation_name, len(foreign_structures_forbidden_ids), foreign_structures_forbidden_ids))
        sys.stdout.flush()

        # Requires role(s): access token
        corp_contracts_data = interface.get_esi_paged_data(
            "corporations/{}/contracts/".format(corporation_id))
        print("\n'{}' corporation has {} contracts".format(corporation_name, len(corp_contracts_data)))
        sys.stdout.flush()

        # Получение подробной информации о каждому из контракту в списке
        corp_contract_items_data = []
        corp_contract_items_len = 0
        corp_contract_items_not_found = []
        if len(corp_contracts_data) > 0:
            # Requires: access token
            for c in corp_contracts_data:
                # для удалённых контрактов нельзя загрузить items (см. ниже 404-ошибку), поэтому пропускаем запись
                if c["status"] == "deleted":
                    continue
                # в рамках работы с чертежами, нас интересует только набор контрактов, в которых продаются чертежи
                # ищем публичные контракты типа "обмен предметами"
                if (c["availability"] != "public") or (c["type"] != "item_exchange"):
                    continue
                # пропускаем контракты на продажу, которые выставили не мы
                # эту настройку лучше не трогать, т.к. во FRT например 12'000 контрактов, следовательно
                # это повлечёт загрузку 12'000 items и 12'000 issuers
                if c['issuer_corporation_id'] != corporation_id:
                    continue
                contract_id = c["contract_id"]
                try:
                    __contract_items = interface.get_esi_data(
                        "corporations/{}/contracts/{}/items/".format(corporation_id, contract_id),
                        fully_trust_cache=True)
                    corp_contract_items_len += len(__contract_items)
                    corp_contract_items_data.append({str(contract_id): __contract_items})
                except requests.exceptions.HTTPError as err:
                    status_code = err.response.status_code
                    if status_code == 404:  # это нормально, что часть доп.инфы по контрактам может быть не найдена!
                        corp_contract_items_not_found.append(contract_id)
                    else:
                        raise
                except:
                    print(sys.exc_info())
                    raise
                # Получение сведений о пилотах, вовлечённых в работу с контрактом
                issuer_id = c["issuer_id"]
                __issuer_dict = next((i for i in various_characters_data if int(list(i.keys())[0]) == int(issuer_id)), None)
                if __issuer_dict is None:
                    # Public information about a character
                    issuer_data = interface.get_esi_data(
                        "characters/{}/".format(issuer_id),
                        fully_trust_cache=True)
                    various_characters_data.append({str(issuer_id): issuer_data})
                sys.stdout.flush()
        eve_esi_tools.dump_debug_into_file(argv_prms["workspace_cache_files_dir"], "corp_contract_items_data.{}".format(corporation_name), corp_contract_items_data)
        eve_esi_tools.dump_debug_into_file(argv_prms["workspace_cache_files_dir"], "various_characters_data", various_characters_data)  # сохраняем м.б. многократно

        print("\n'{}' corporation has {} items in contracts".format(corporation_name, corp_contract_items_len))
        if len(corp_contract_items_not_found) > 0:
            print("'{}' corporation has {} contracts without details : {}".format(corporation_name, len(corp_contract_items_not_found), corp_contract_items_not_found))
        sys.stdout.flush()

        # Построение дерева ассетов, с узлави в роли станций и систем, и листьями в роли хранящихся
        # элементов, в виде:
        # { location1: {items:[item1,item2,...],type_id,location_id},
        #   location2: {items:[item3],type_id} }
        corp_assets_tree = eve_esi_tools.get_assets_tree(corp_assets_data, foreign_structures_data, sde_inv_items, virtual_hierarchy_by_corpsag=False)
        eve_esi_tools.dump_debug_into_file(argv_prms["workspace_cache_files_dir"], "corp_assets_tree.{}".format(corporation_name), corp_assets_tree)

        # Построение дерева имущества (сводная информация, учитывающая объёмы и ориентировочную стоимость asset-ов)
        print("\nBuilding {} blueprints stat...".format(corporation_name))
        sys.stdout.flush()
        corp_blueprints, blueprints_locations = __build_blueprints(
            corp_blueprints_data,
            corp_industry_jobs_data,
            eve_market_prices_data,
            corp_contracts_data,
            corp_contract_items_data,
            various_characters_data,
            sde_type_ids,
            sde_inv_names,
            sde_inv_items,
            sde_market_groups,
            corp_assets_tree,
            corp_ass_names_data,
            foreign_structures_data)

        corp_blueprints.sort(key=lambda bp: bp["name"])

        corps_blueprints.update({str(corporation_id): {
            "corporation": corporation_name,
            "blueprints": corp_blueprints,
            "locations": blueprints_locations
        }})

    eve_esi_tools.dump_debug_into_file(argv_prms["workspace_cache_files_dir"], "corps_blueprints", corps_blueprints)

    print("\nBuilding blueprints reports...")
    sys.stdout.flush()

    render_html_blueprints.dump_blueprints_into_report(
        # путь, где будет сохранён отчёт
        argv_prms["workspace_cache_files_dir"],
        # данные, полученные в результате анализа и перекомпоновки входных списков
        corps_blueprints
    )

    # Вывод в лог уведомления, что всё завершилось (для отслеживания с помощью tail)
    print("\nDone")


if __name__ == "__main__":
    main()
