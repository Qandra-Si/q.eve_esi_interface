﻿""" Q.Dictionaries (desktop/mobile)

Prerequisites:
    * Have a Python 3 environment available to you (possibly by using a
      virtual environment: https://virtualenv.pypa.io/en/stable/).
    * Run pip install -r requirements.txt --user with this directory.
      or
      Run pip install -r requirements.txt with this directory as your root.

    * Copy q_industrialist_settings.py.template into q_industrialist_settings.py and
      mood for your needs.
    * Create an SSO application at developers.eveonline.com with the scopes
      from g_client_scope list declared in q_industrialist_settings.py and the
      callback URL "https://localhost/callback/".
      Note: never use localhost as a callback in released applications.

$ chcp 65001 & @rem on Windows only!
$ python eve_sde_tools.py --cache_dir=~/.q_industrialist
$ python q_dictionaries.py --category=all --cache_dir=~/.q_industrialist
"""
import sys
import getopt
import typing

import q_industrialist_settings
import q_router_settings
import postgresql_interface as db
import eve_sde_tools
import eve_router_tools
import eve_industry_profit
import profit


def main():
    possible_categories = [
        # запуск скрипта со вводом всех возможных данных в БД (крайне не рекомендуется
        # запускать в этом режиме без необходимости, т.к. часть данных актуализируется по
        # ESI будучи первично добавлено этим скриптом, что к сожалению порой занимает много
        # времени)
        'all',
        # быстрый и унифицированный справочник по названиям, используемым во вселенной,
        # который разделяется по категориям в зависимости от типа
        'names',
        # справочник по celestial объёктам вселенной (регионы, констелляции, системы, луны...)
        'items',
        # ввод данных по чертежам, продуктам производста, типам произвосдва и материалам,
        # используемым при работе с чертежами (данные не могут быть получены по ESI), поэтому
        # это единстенный способ актаулизации информации при обновлении во вселейнной)
        'blueprints',
        # ввод данных по категориям групп предметов во вселенной
        'categories',
        # ввод данных по группам предметов во вселенной
        'groups',
        # ввод данных по типам во вселенной (впоследствии актуализируется автоматически по ESI,
        # а также дополняется параметром packaged_volume (что является очень длительной процедурой
        # и крайне не рекомендуются запускать скрипт с этим параметром без необходимости)
        'type_ids',
        # ввод данных по market группам, которые хранятся в БД в рекурсивном виде и хранят также
        # семантику по подтипам в зависимости от полезности группы (например все виды патронов
        # семантически относятся к патронам, а все виды руд, минералов относятся к материалам)
        'market_groups',
        # ввод данных по чертежам, расчёт стоимости работ с учётом используемых материалов и
        # стоимости запуска работ, выполняются всякий раз при обновлении информации о чертежах
        'conveyor_formulas',
    ]

    exit_or_wrong_getopt = None
    workspace_cache_files_dir = None
    category = None
    try:
        opts, args = getopt.getopt(sys.argv[1:], "h", ["help", "cache_dir=", "category="])
    except getopt.GetoptError:
        exit_or_wrong_getopt = 2
    if exit_or_wrong_getopt is None:
        for opt, arg in opts:  # noqa
            if opt in ('-h', "--help"):
                exit_or_wrong_getopt = 0
                break
            elif opt in ("--cache_dir"):
                workspace_cache_files_dir = arg[:-1] if arg[-1:] == '/' else arg
            elif opt in ("--category"):
                category = arg
        if workspace_cache_files_dir is None:
            exit_or_wrong_getopt = 0
        if not category or (category not in possible_categories):
            exit_or_wrong_getopt = 1
    if not (exit_or_wrong_getopt is None):
        print("Usage: {app} --category=names --cache_dir=/tmp\n"
              "Possible categories: {cats}\n"
              "Don't use 'type_ids' or 'all' category indiscriminately (too much afterward overheads)!".
              format(app=sys.argv[0], cats=possible_categories))
        sys.exit(exit_or_wrong_getopt)

    qidb = db.QIndustrialistDatabase("dictionaries", debug=False)
    qidb.connect(q_industrialist_settings.g_database)
    qidbdics = db.QDictionaries(qidb)

    if category in ['all', 'names']:
        sde_meta_groups = eve_sde_tools.read_converted(workspace_cache_files_dir, "metaGroups")
        qidbdics.actualize_names(sde_meta_groups, 0, "nameID")
        del sde_meta_groups

        sde_type_ids = eve_sde_tools.read_converted(workspace_cache_files_dir, "typeIDs")
        qidbdics.actualize_names(sde_type_ids, 1, "name")
        del sde_type_ids

        sde_market_groups = eve_sde_tools.read_converted(workspace_cache_files_dir, "marketGroups")
        qidbdics.actualize_names(sde_market_groups, 2, "nameID")
        del sde_market_groups

        sde_inv_names = eve_sde_tools.read_converted(workspace_cache_files_dir, "invNames")
        qidbdics.actualize_names(sde_inv_names, 3, None)
        del sde_inv_names

        # [1..6] : https://support.eveonline.com/hc/en-us/articles/203210272-Activities-and-Job-Types
        # [0,1,3,4,5,7,8,11, +9?] : https://github.com/esi/esi-issues/issues/894
        qidbdics.clean_names(4)
        qidbdics.insert_name(1, 4, "manufacturing")  # Manufacturing
        qidbdics.insert_name(3, 4, "te")  # Science
        qidbdics.insert_name(4, 4, "me")  # Science
        qidbdics.insert_name(5, 4, "copying")  # Science
        qidbdics.insert_name(7, 4, "reverse")  # Science
        qidbdics.insert_name(8, 4, "invention")  # Science
        qidbdics.insert_name(9, 4, "reaction")  # Reaction
        qidbdics.insert_name(11, 4, "reaction")  # Reaction
        qidb.commit()

        qidbdics.clean_integers(5)
        qidbdics.clean_integers(6)
        qidbdics.clean_integers(7)
        sde_blueprints = eve_sde_tools.read_converted(workspace_cache_files_dir, "blueprints")
        for bp in sde_blueprints.items():
            __blueprint_type_id = int(bp[0])
            __bpa = bp[1].get("activities", None)
            if __bpa is None:
                continue
            __bpam = __bpa.get("manufacturing", None)
            __bpai = __bpa.get("invention", None)
            __bpar = __bpa.get("reaction", None)
            if __bpam is not None:
                if "products" in __bpam:
                    __products_quantity = __bpam["products"][0]["quantity"]
                    qidbdics.insert_integer(__blueprint_type_id, 5, __products_quantity)
            if __bpai is not None:
                if "products" in __bpai:
                    __products_quantity = __bpai["products"][0]["quantity"]
                    qidbdics.insert_integer(__blueprint_type_id, 6, __products_quantity)
            if __bpar is not None:
                if "products" in __bpar:
                    __products_quantity = __bpar["products"][0]["quantity"]
                    qidbdics.insert_integer(__blueprint_type_id, 7, __products_quantity)
        # qidbdics.actualize_names(sde_meta_groups, 0, "nameID")
        del sde_blueprints

    if category in ['all', 'blueprints']:
        sde_blueprints = eve_sde_tools.read_converted(workspace_cache_files_dir, "blueprints")
        qidbdics.clean_blueprints()
        qidbdics.actualize_blueprints(sde_blueprints)
        del sde_blueprints

    # при удалении type_ids, market_groups, groups и categories важно соблюсти последовательность
    # с тем, чтобы каскадоне удаление данных из связанных таблиц не уничтожало только что
    # добавленные данные

    if category in ['all', 'categories']:
        sde_categories = eve_sde_tools.read_converted(workspace_cache_files_dir, "categoryIDs")
        #qidbdics.clean_categories()
        qidbdics.actualize_categories(sde_categories)
        del sde_categories

    if category in ['all', 'groups']:
        sde_groups = eve_sde_tools.read_converted(workspace_cache_files_dir, "groupIDs")
        #qidbdics.clean_groups()
        qidbdics.actualize_groups(sde_groups)
        del sde_groups

    if category in ['all', 'market_groups']:
        sde_market_groups = eve_sde_tools.read_converted(workspace_cache_files_dir, "marketGroups")
        sde_market_groups_keys = sde_market_groups.keys()
        for group_id in sde_market_groups_keys:
            mg = sde_market_groups[str(group_id)]
            group_id: int = int(group_id)
            semantic_id = eve_sde_tools.get_basis_market_group_by_group_id(sde_market_groups, group_id)
            mg.update({'semanticGroupID': semantic_id if semantic_id else group_id})
        del sde_market_groups_keys
        #qidbdics.clean_market_groups()
        qidbdics.actualize_market_groups(sde_market_groups)
        del sde_market_groups

    if category in ['all', 'type_ids']:
        user_choice = input("Are you sure to cleanup type_ids in database?\n"
                            "Too much afterward overheads!!!\n"
                            "Please type 'yes': ")
        if user_choice == 'yes':
            sde_type_ids = eve_sde_tools.read_converted(workspace_cache_files_dir, "typeIDs")
            qidbdics.actualize_type_ids(sde_type_ids)
            del sde_type_ids
            
    if category in ['all', 'conveyor_formulas']:
        user_choice = input("Are you sure to cleanup conveyor_formulas in database?\n"
                            "Too much afterward overheads!!!\n"
                            "Please type 'yes' or 'append': ")
        if user_choice == 'yes' or user_choice == 'append':
            sde_type_ids = eve_sde_tools.read_converted(workspace_cache_files_dir, "typeIDs")
            sde_market_groups = eve_sde_tools.read_converted(workspace_cache_files_dir, "marketGroups")
            sde_groups = eve_sde_tools.read_converted(workspace_cache_files_dir, "groupIDs")
            sde_blueprints = eve_sde_tools.read_converted(workspace_cache_files_dir, "blueprints")
            sde_inv_names = eve_sde_tools.read_converted(workspace_cache_files_dir, "invNames")
            sde_products = eve_sde_tools.construct_products_for_blueprints(sde_blueprints, sde_type_ids)

            eve_router_tools.combine_router_outputs(
                q_router_settings.g_routes,
                sde_groups, sde_type_ids, sde_market_groups)

            # TODO: генерируем фейковые данные
            eve_market_prices_data = []
            # TODO: генерируем фейковые данные
            eve_industry_systems_data = []
            for r in q_router_settings.g_routes:
                assert 'solar_system' in r
                solar_system: str = r['solar_system']
                solar_system_id: typing.Optional[int] = next((int(_[0]) for _ in sde_inv_names.items()
                                                              if _[1] == solar_system), None)
                if [_ for _ in eve_industry_systems_data if _['solar_system_id'] == solar_system_id]: continue
                eve_industry_systems_data.append({
                    "cost_indices": [
                        {"activity": "manufacturing", "cost_index": 0.0014},
                        {"activity": "researching_time_efficiency", "cost_index": 0.0014},
                        {"activity": "researching_material_efficiency", "cost_index": 0.0014},
                        {"activity": "copying", "cost_index": 0.0014},
                        {"activity": "invention", "cost_index": 0.0014},
                        {"activity": "reaction", "cost_index": 0.0014}
                    ],
                    "solar_system_id": solar_system_id
                })

            # индексы стоимости производства для различных систем (системы и продукция заданы в настройках роутинга)
            industry_cost_indices: typing.List[profit.QIndustryCostIndices] = []
            for r in q_router_settings.g_routes:
                assert 'solar_system' in r
                solar_system: str = r['solar_system']
                solar_system_id: typing.Optional[int] = next((int(_[0]) for _ in sde_inv_names.items()
                                                              if _[1] == solar_system), None)
                assert solar_system_id is not None
                cost_indices = next((_['cost_indices'] for _ in eve_industry_systems_data
                                     if _['solar_system_id'] == solar_system_id), None)
                assert cost_indices is not None
                assert 'structure' in r
                factory_bonuses: profit.QIndustryFactoryBonuses = profit.QIndustryFactoryBonuses(
                    r['structure'],
                    r.get('structure_rigs', []))
                iic: profit.QIndustryCostIndices = profit.QIndustryCostIndices(
                    solar_system_id,
                    solar_system,
                    cost_indices,
                    r['station'],
                    r['output'],
                    factory_bonuses)
                industry_cost_indices.append(iic)

            # удаление более ненужных списков
            del eve_industry_systems_data
            del sde_inv_names

            # см. также eve_conveyor_tools.py : setup_blueprint_details
            # см. также q_industry_profit.py : main
            # см. также q_dictionaries.py : main
            icc = q_industrialist_settings.g_industry_calc_customization
            industry_plan_customization = profit.QIndustryPlanCustomization(
                # длительность всех реакций - около 1 суток
                reaction_runs=icc.get('reaction_runs', 15),
                # длительность производства компонентов общего потребления (таких как Advanced Components или
                # Fuel Blocks) тоже принимается около 1 суток, остальные материалы рассчитываются в том объёме,
                # в котором необходимо
                industry_time=icc.get('industry_time', 5*60*60*24),
                # market-группы компонентов общего потребления
                common_components=icc.get('common_components', [
                    1870,  # Fuel Blocks
                    65,    # Advanced Components
                    1883,  # Advanced Capital Components
                    2768,  # Protective Components
                    1908,  # R.A.M.
                    1147,  # Subsystem Components
                ]),
                # * 18% jump freighters; 22% battleships; 26% cruisers, BCs, industrial, mining barges;
                #   30% frigate hull, destroyer hull; 34% modules, ammo, drones, rigs
                # * Tech 3 cruiser hulls and subsystems have 22%, 30% or 34% chance depending on artifact used
                # * Tech 3 destroyer hulls have 26%, 35% or 39% chance depending on artifact used
                # рекомендации к минимальным скилам: 3+3+3 (27..30% навыки и импланты)
                # Invention_Chance =
                #  Base_Chance *
                #  (1 + ((Encryption_Skill_Level / 40) +
                #        ((Datacore_1_Skill_Level + Datacore_2_Skill_Level) / 30)
                #       )
                #  ) * Decryptor_Modifier
                # 27.5% => min навыки и импланты пилотов запускающих инвенты (вся научка мин в 3)
                min_probability=icc.get('min_probability', 27.5),
                # экономия материалов (material efficiency) промежуточных чертежей
                unknown_blueprints_me=icc.get('unknown_blueprints_me', 10),
                # экономия времени (time efficiency) промежуточных чертежей
                unknown_blueprints_te=icc.get('unknown_blueprints_te', 20))

            # автоматический выбор чертежей для их расчёта и загрузки в БД
            possible_decryptors: typing.List[profit.QPossibleDecryptor] = profit.get_list_of_decryptors()
            calc_inputs: typing.List[typing.Dict[str, int]] = []
            for key in sde_blueprints.keys():
                # ограничитель: if len(calc_inputs) >= 10: break
                tid = sde_type_ids.get(key)
                if not tid: continue
                if not tid.get('published', False): continue  # Clone Grade Beta Blueprint
                blueprint = sde_blueprints[key]
                blueprint_type_id: int = int(key)
                # проверка, возможно ли производство по этому чертежу?
                if 'manufacturing' in blueprint['activities']:
                    assert len(blueprint['activities']['manufacturing']['products']) == 1
                    product_type_id = blueprint['activities']['manufacturing']['products'][0]['typeID']
                    product_tid = sde_type_ids.get(str(product_type_id))
                    if product_tid.get('published', False):  # тут м.б. Haunter Cruise Missile
                        # проверяем, может быть нам попался фракционный чертёж? если да, то me=0, te=0
                        # фракционные чертежи отличаются тем, что не имеют никаких производственных
                        # активностей, кроме manufacturing, и сами не являются продуктом другого
                        # производства
                        if len(blueprint['activities']) == 1:
                            is_any_prior_blueprint: typing.Optional[int] = \
                                next((1 for _ in sde_products.values() if blueprint_type_id in _.keys()), None)
                            # если предыдущего чертежа в цепочке производства нет, то это фракционный BPC
                            if is_any_prior_blueprint is None:
                                # print('Fractional blueprint copy: ', tid['name']['en'])
                                calc_inputs.append({
                                    'bptid': blueprint_type_id,
                                    'qr': 1,
                                    'me': 0,
                                    'te': 0})
                                continue
                        # продолжаем просматривать чертежи по группам, может быть это супера?
                        if 'groupID' in product_tid:
                            product_group_id: int = product_tid['groupID']
                            if product_group_id in [
                                30,  # Titan
                                659,  # Supercarrier
                                1538,  # Force Auxiliary
                                547,  # Carrier
                                # нельзя, здесь все кораблики T2 уровня: 4594,  # Lancer Dreadnought
                                485,  # Dreadnought
                                883,  # Capital Industrial Ship
                                # нельзя, здесь все кораблики Т2 уровня: 902,  # Jump Freighter
                                1657,  # Citadel
                                513,  # Freighter
                            ]:
                                calc_inputs.append({
                                    'bptid': blueprint_type_id,
                                    'qr': 1,
                                    'me': 0,
                                    'te': 0})
                                is_original: bool = 'research_material' in blueprint['activities']
                                if is_original:
                                    # TODO: также следует проверять blueprint['maxProductionLimit']
                                    for me in range(1, 10+1):
                                        calc_inputs.append({
                                            'bptid': blueprint_type_id,
                                            'qr': 1,
                                            'me': me,
                                            'te': me * 2})  # te не влияет на расчёты профита
                            elif product_group_id in [
                                334,  # Construction Component #334 (апгрейд чертежа до me=10, te=20)
                                913,  # Advanced Capital Construction Components #913 (аналогично)
                                1136  # Fuel Block #1136 (аналогично)
                            ]:
                                manufacturing = blueprint['activities']['manufacturing']
                                need_quantity: int = 1
                                single_run_time: int = manufacturing['time']
                                products_per_single_run: int = manufacturing['products'][0]['quantity']
                                is_commonly_used: bool = True
                                bpos, runs = eve_industry_profit.get_optimized_runs_quantity__manufacturing(
                                    need_quantity,
                                    single_run_time,
                                    products_per_single_run,
                                    is_commonly_used,
                                    industry_plan_customization.industry_time)
                                calc_inputs.append({
                                    'bptid': blueprint_type_id,
                                    'qr': runs,
                                    'me': 10,
                                    'te': 20})
                # проверка, возможен ли инвент чертежей?
                if 'invention' in blueprint['activities']:
                    if 'products' in blueprint['activities']['invention']:  # тут м.б. Coalesced Element Blueprint
                        for t2_blueprint_invent in blueprint['activities']['invention']['products']:
                            t2_blueprint_type_id: int = t2_blueprint_invent['typeID']
                            # if t2_blueprint_type_id != 54850: continue
                            t2_blueprint_runs: int = t2_blueprint_invent['quantity']
                            t2_blueprint_tid = sde_type_ids.get(str(t2_blueprint_type_id))
                            if t2_blueprint_tid and t2_blueprint_tid.get('published', False):
                                t2_blueprint = sde_blueprints.get(str(t2_blueprint_type_id))
                                if t2_blueprint and 'manufacturing' in t2_blueprint['activities']:
                                    assert len(t2_blueprint['activities']['manufacturing']['products']) == 1
                                    t2_product = t2_blueprint['activities']['manufacturing']['products'][0]
                                    t2_product_type_id: int = t2_product['typeID']
                                    t2_product_tid = sde_type_ids.get(str(t2_product_type_id))
                                    if t2_product_tid.get('published', False):
                                        # print(t2_blueprint_type_id, t2_blueprint_tid['name']['en'])
                                        meta_group_id: int = t2_product_tid.get('metaGroupID')
                                        assert meta_group_id
                                        if meta_group_id in {2, 53}:  # Tech II, Structure Tech II
                                            for d in possible_decryptors:
                                                calc_inputs.append({
                                                    'bptid': t2_blueprint_type_id,
                                                    'qr': t2_blueprint_runs + d.runs,
                                                    'me': 2 + d.me,
                                                    'te': 4 + d.te,
                                                    'bpc': blueprint_type_id})
                                        elif meta_group_id == 14:  # Tech III
                                            # for d in possible_decryptors:
                                            #    calc_inputs.append({
                                            #        'bptid': t2_blueprint_type_id,
                                            #        'qr': t2_blueprint['maxProductionLimit'] + d.runs,
                                            #        'me': 2 + d.me,
                                            #        'te': 3 + d.te,
                                            #        'bpc': blueprint_type_id})
                                            pass
                                        else:
                                            assert 0

            # в том случае, если invent невозможен, то проверяем что чертёж (1) не продаётся в маркете,
            # (2) опубликован, (3) не является продуктом инвента, его (4) продукция опубликована
            for key in sde_blueprints.keys():
                # ограничитель: if len(calc_inputs) >= 10: break
                tid = sde_type_ids.get(key)
                if not tid: continue
                if not tid.get('published', False): continue  # Clone Grade Beta Blueprint
                if tid.get('marketGroupID') is not None: continue
                blueprint = sde_blueprints[key]
                if 'invention' in blueprint['activities']: continue
                blueprint_type_id: int = int(key)
                if sde_products['invention'].get(blueprint_type_id) is not None: continue
                # проверка, возможно ли производство по этому чертежу?
                if 'manufacturing' in blueprint['activities']:
                    if 'materials' not in blueprint['activities']['manufacturing']: continue  # Apotheosis Blueprint
                    assert len(blueprint['activities']['manufacturing']['products']) == 1
                    product_type_id = blueprint['activities']['manufacturing']['products'][0]['typeID']
                    product_tid = sde_type_ids.get(str(product_type_id))
                    if product_tid.get('published', False):  # тут м.б. Haunter Cruise Missile
                        """
                        -- поиск фракционных чертежей, которые продаются только в контрактах
                        select
                         bid.sdet_type_name, -- x.*,
                         pid.sdet_type_name, -- p.*,
                         bid.sdet_meta_group_id,
                         (SELECT sden_name FROM qi.eve_sde_names WHERE sden_category=0 and sden_id=bid.sdet_meta_group_id)
                        from
                         qi.eve_sde_blueprints x,
                         qi.eve_sde_blueprint_products p,
                         qi.eve_sde_type_ids bid,
                         qi.eve_sde_type_ids pid
                        where 
                         bid.sdet_market_group_id is null and
                         x.sdeb_blueprint_type_id=bid.sdet_type_id and
                         bid.sdet_published and
                         x.sdeb_activity=1 and
                         x.sdeb_blueprint_type_id not in (select sdeb_blueprint_type_id from qi.eve_sde_blueprints where sdeb_activity=8) and
                         x.sdeb_blueprint_type_id not in (select sdebp_product_id from qi.eve_sde_blueprint_products where sdebp_activity=8) and
                         x.sdeb_blueprint_type_id in (select distinct sdebm_blueprint_type_id from qi.eve_sde_blueprint_materials) and
                         p.sdebp_blueprint_type_id=x.sdeb_blueprint_type_id and
                         p.sdebp_activity=1 and
                         p.sdebp_product_id=pid.sdet_type_id and
                         pid.sdet_published
                        order by pid.sdet_type_name
                        """
                        if not next((1 for _ in calc_inputs if _['bptid'] == blueprint_type_id), None):
                            # print(tid['name']['en'])
                            calc_inputs.append({
                                'bptid': blueprint_type_id,
                                'qr': 1,
                                'me': 0,
                                'te': 0})

            if user_choice == 'yes':
                qidbdics.clean_conveyor_formulas()
            else:
                exists: typing.List[typing.Dict[str, int]] = qidbdics.get_existed_conveyor_formulas()
                calc_inputs = list(filter(lambda _: _ not in exists, calc_inputs))

            calc_num: int = 0
            for calc_input in calc_inputs:
                conveyor_formula: typing.Optional[profit.QIndustryFormula] = None
                try:
                    # выходные данные после расчёта: дерево материалов и работ, которые надо выполнить
                    industry_tree: typing.Optional[profit.QIndustryTree] = eve_industry_profit.generate_industry_tree(
                        # вход и выход для расчёта
                        calc_input,
                        industry_plan_customization,
                        # sde данные, загруженные из .converted_xxx.json файлов
                        sde_type_ids,
                        sde_blueprints,
                        sde_products,
                        sde_market_groups,
                        eve_market_prices_data,
                        industry_cost_indices)

                    # проверка на странные чертежи типа:
                    # Thukker Component Assembly Array Blueprint (33868) - производится то, что требуется в материалах
                    if industry_tree is None:
                        continue

                    # выходные данные после расчёта: список материалов и ratio-показатели их расхода для
                    # производства qr-ранов
                    industry_plan: profit.QIndustryPlan = eve_industry_profit.generate_industry_plan(
                        industry_tree.blueprint_runs_per_single_copy,
                        industry_tree,
                        industry_plan_customization)

                    conveyor_formula: typing.Optional[profit.QIndustryFormula] = \
                        eve_industry_profit.assemble_industry_formula(industry_plan)

                    qidbdics.actualize_conveyor_formula(conveyor_formula)
                except:
                    if conveyor_formula:
                        print('Input:',
                              calc_input,
                              'Product:',
                              conveyor_formula.product_type_id,
                              'Runs:',
                              conveyor_formula.customized_runs,
                              'Decryptor:',
                              conveyor_formula.decryptor_type_id)
                    else:
                        print('Input:', calc_input)
                    raise

                calc_num += 1
                if (calc_num % 20) == 0:
                    print(f'Progress: {100.0 * (calc_num / len(calc_inputs)):.1f}%')
                    sys.stdout.flush()

            del sde_blueprints
            del sde_market_groups
            del sde_type_ids

    if category in ['all', 'items']:
        sde_inv_items = eve_sde_tools.read_converted(workspace_cache_files_dir, "invItems")
        qidbdics.clean_items()
        qidbdics.actualize_items(sde_inv_items)
        del sde_inv_items

    del qidbdics
    del qidb
    sys.exit(0)  # code 0, all ok


if __name__ == "__main__":
    main()
