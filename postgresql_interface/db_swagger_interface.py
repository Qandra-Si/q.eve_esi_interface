﻿# -*- encoding: utf-8 -*-
import pytz


class QSwaggerInterface:
    def __init__(self, db):
        """ constructor

        :param db: instance of QIndustrialistDatabase
        """
        self.db = db

    def __del__(self):
        """ destructor
        """

    # -------------------------------------------------------------------------
    # u n i v e r s a l
    # -------------------------------------------------------------------------

    def is_exist_something(self, id, table, field):
        """
        :param table: table name
        :param field: field name
        :return: true - exist, false - absent
        """
        sdenid = self.db.select_one_row("SELECT 1 FROM {f} WHERE {t}=%s;".format(t=table, f=field), id)
        if sdenid is None:
            return False
        return True

    def get_exist_ids(self, table, field, updated):
        """
        :param table: table name
        :param field: field name of identity
        :param updated: field name of updated_at
        :return: list of unique identities stored in the database
        """
        aids = self.db.select_all_rows("SELECT {f},{u} FROM {t};".format(t=table, f=field, u=updated))
        return aids

    def get_absent_ids(self, ids, table, field):
        """
        :param ids: list of unique identities to compare with ids, stored in the database
        :param table: table name
        :param field: field name
        :return: list of ids which are not in the database
        """
        aids = self.db.select_all_rows(
            "SELECT id FROM UNNEST(%s) AS a(id) "
            "WHERE id NOT IN (SELECT {f} FROM {t});".format(t=table, f=field),
            ids
        )
        return aids

    # -------------------------------------------------------------------------
    # characters/{character_id}/
    # -------------------------------------------------------------------------

    def is_exist_character_id(self, id):
        return self.is_exist_something(id, 'esi_characters', 'ech_character_id')

    def get_exist_character_ids(self):
        return self.get_exist_ids('esi_characters', 'ech_character_id', 'ech_updated_at')

    def get_absent_character_ids(self, ids):
        return self.get_absent_ids(ids, 'esi_characters', 'ech_character_id')

    def insert_or_update_character(self, id, data, updated_at):
        """ inserts character data into database

        :param id: unique character id
        :param data: character data
        :param updated_at: :class:`datetime.datetime`
        """
        # { "alliance_id": 99010134,
        #   "ancestry_id": 4,
        #   "birthday": "2009-08-19T19:23:00Z",
        #   "bloodline_id": 6,
        #   "corporation_id": 98553333,
        #   "description": "...",
        #   "gender": "male",
        #   "name": "olegez",
        #   "race_id": 4,
        #   "security_status": 3.960657443
        #  }
        self.db.execute(
            "INSERT INTO esi_characters("
            " ech_character_id,"
            " ech_name,"
            " ech_corporation_id,"
            " ech_birthday,"
            " ech_created_at,"
            " ech_updated_at) "
            "VALUES("
            " %(id)s,"
            " %(nm)s,"
            " %(co)s,"
            " %(bth)s,"
            " CURRENT_TIMESTAMP AT TIME ZONE 'GMT',"
            " TIMESTAMP WITHOUT TIME ZONE %(at)s) "
            "ON CONFLICT ON CONSTRAINT pk_ech DO UPDATE SET"
            " ech_corporation_id=%(co)s,"
            " ech_updated_at=TIMESTAMP WITHOUT TIME ZONE %(at)s;",
            {'id': id,
             'nm': data['name'],
             'co': data['corporation_id'],
             'bth': data['birthday'],
             'at': updated_at,
             }
        )

    def select_character(self, id):
        row = self.db.select_one_row(
            "SELECT ech_name,ech_corporation_id,ech_birthday,ech_updated_at "
            "FROM esi_characters "
            "WHERE ech_character_id=%s;",
            id
        )
        if row is None:
            return None, None
        return {'name': row[0], 'corporation_id': row[1], 'birthday': row[2]}, row[3]

    # -------------------------------------------------------------------------
    # corporations/{corporation_id}/
    # -------------------------------------------------------------------------

    def is_exist_corporation_id(self, id):
        return self.is_exist_something(id, 'esi_corporations', 'eco_corporation_id')

    def get_exist_corporation_ids(self):
        return self.get_exist_ids('esi_corporations', 'eco_corporation_id', 'eco_updated_at')

    def get_absent_corporation_ids(self, ids):
        return self.get_absent_ids(ids, 'esi_corporations', 'eco_corporation_id')

    def insert_or_update_corporation(self, id, data, updated_at):
        """ inserts corporation data into database

        :param id: unique corporation id
        :param data: corporation data
        :param updated_at: :class:`datetime.datetime`
        """
        # { "alliance_id": 99007203,
        #   "ceo_id": 93531267,
        #   "creator_id": 93362315,
        #   "date_founded": "2019-09-27T20:27:54Z",
        #   "description": "...",
        #   "home_station_id": 60003064,
        #   "member_count": 215,
        #   "name": "R Initiative 4",
        #   "shares": 1000,
        #   "tax_rate": 0.1,
        #   "ticker": "RI4",
        #   "url": "",
        #   "war_eligible": true
        #  }
        self.db.execute(
            "INSERT INTO esi_corporations("
            " eco_corporation_id,"
            " eco_name,"
            " eco_ticker,"
            " eco_member_count,"
            " eco_ceo_id,"
            " eco_alliance_id,"
            " eco_tax_rate,"
            " eco_creator_id,"
            " eco_home_station_id,"
            " eco_shares,"
            " eco_created_at,"
            " eco_updated_at) "
            "VALUES ("
            " %(id)s,"
            " %(nm)s,"
            " %(ti)s,"
            " %(mem)s,"
            " %(ceo)s,"
            " %(ali)s,"
            " %(tax)s,"
            " %(own)s,"
            " %(hm)s,"
            " %(sh)s,"
            " CURRENT_TIMESTAMP AT TIME ZONE 'GMT',"
            " TIMESTAMP WITHOUT TIME ZONE %(at)s) "
            "ON CONFLICT ON CONSTRAINT pk_eco DO UPDATE SET"
            " eco_name=%(nm)s,"
            " eco_ticker=%(ti)s,"
            " eco_member_count=%(mem)s,"
            " eco_ceo_id=%(ceo)s,"
            " eco_alliance_id=%(ali)s,"
            " eco_tax_rate=%(tax)s,"
            " eco_home_station_id=%(hm)s,"
            " eco_shares=%(sh)s,"
            " eco_updated_at=TIMESTAMP WITHOUT TIME ZONE %(at)s;",
            {'id': id,
             'nm': data['name'],
             'ti': data['ticker'],
             'mem': data['member_count'],
             'ceo': data['ceo_id'],
             'ali': data.get('alliance_id', None),
             'tax': data['tax_rate'],
             'own': data['creator_id'],
             'hm': data.get('home_station_id', None),
             'sh': data.get('shares', None),
             'at': updated_at,
             }
        )

    def select_corporation(self, id):
        row = self.db.select_one_row(
            "SELECT eco_name,eco_ticker,eco_member_count,eco_ceo_id,eco_alliance_id,eco_tax_rate,"
            " eco_creator_id,eco_home_station_id,eco_shares,eco_updated_at "
            "FROM esi_corporations "
            "WHERE eco_corporation_id=%s;",
            id
        )
        if row is None:
            return None, None
        data = {
            'name': row[0],
            'ticker': row[1],
            'member_count': row[2],
            'ceo_id': row[3],
            'tax_rate': row[5],
            'creator_id': row[6],
            'shares': row[8]
        }
        if row[4]:
            data.update({'alliance_id': row[4]})
        if row[7]:
            data.update({'home_station_id': row[7]})
        return data, row[9]

    # -------------------------------------------------------------------------
    # universe/stations/
    # -------------------------------------------------------------------------

    def is_exist_station_id(self, id):
        return self.is_exist_something(id, 'esi_tranquility_stations', 'ets_station_id')

    def get_exist_universe_station_ids(self):
        return self.get_exist_ids('esi_tranquility_stations', 'ets_station_id', 'ets_updated_at')

    def get_absent_universe_station_ids(self, ids):
        return self.get_absent_ids(ids, 'esi_tranquility_stations', 'ets_station_id')

    def insert_or_update_universe_station(self, data, updated_at):
        """ inserts universe station data into database

        :param data: universe station data
        :param updated_at: :class:`datetime.datetime`
        """
        # { "max_dockable_ship_volume": 50000000,
        #   "name": "Jakanerva III - Moon 15 - Prompt Delivery Storage",
        #   "office_rental_cost": 10000,
        #   "owner": 1000003,
        #   "position": {
        #     "x": 165632286720,
        #     "y": 2771804160,
        #     "z": -2455331266560
        #   },
        #   "race_id": 1,
        #   "reprocessing_efficiency": 0.5,
        #   "reprocessing_stations_take": 0.05,
        #   "services": [
        #     "courier-missions",
        #     "reprocessing-plant",
        #     "market",
        #     "repair-facilities",
        #     "fitting",
        #     "news",
        #     "storage",
        #     "insurance",
        #     "docking",
        #     "office-rental",
        #     "loyalty-point-store",
        #     "navy-offices"
        #   ],
        #   "station_id": 60000277,
        #   "system_id": 30000148,
        #   "type_id": 1531
        # }
        self.db.execute(
            "INSERT INTO esi_tranquility_stations("
            " ets_station_id,"
            " ets_type_id,"
            " ets_name,"
            " ets_owner_id,"
            " ets_race_id,"
            " ets_x,ets_y,ets_z,"
            " ets_system_id,"
            " ets_reprocessing_efficiency,"
            " ets_reprocessing_stations_take,"
            " ets_max_dockable_ship_volume,"
            " ets_office_rental_cost,"
            " ets_created_at,"
            " ets_updated_at) "
            "VALUES ("
            " %(id)s,"
            " %(ty)s,"
            " %(nm)s,"
            " %(own)s,"
            " %(rc)s,"
            " %(x)s,%(y)s,%(z)s,"
            " %(ss)s,"
            " %(re)s,"
            " %(rt)s,"
            " %(vol)s,"
            " %(rnt)s,"
            " CURRENT_TIMESTAMP AT TIME ZONE 'GMT',"
            " TIMESTAMP WITHOUT TIME ZONE %(at)s) "
            "ON CONFLICT ON CONSTRAINT pk_ets DO UPDATE SET"
            " ets_type_id=%(ty)s,"
            " ets_name=%(nm)s,"
            " ets_owner_id=%(own)s,"
            " ets_race_id=%(rc)s,"
            " ets_x=%(x)s,ets_y=%(y)s,ets_z=%(z)s,"
            " ets_system_id=%(ss)s,"
            " ets_reprocessing_efficiency=%(re)s,"
            " ets_reprocessing_stations_take=%(rt)s,"
            " ets_max_dockable_ship_volume=%(vol)s,"
            " ets_office_rental_cost=%(rnt)s,"
            " ets_updated_at=TIMESTAMP WITHOUT TIME ZONE %(at)s;",
            {'id': data['station_id'],
             'ty': data['type_id'],
             'nm': data['name'],
             'own': data.get('owner', None),  # ID of the corporation that controls this station
             'rc': data.get('race_id', None),
             'x': data['position']['x'],
             'y': data['position']['y'],
             'z': data['position']['z'],
             'ss': data['system_id'],
             're': data['reprocessing_efficiency'],
             'rt': data['reprocessing_stations_take'],
             'vol': data['max_dockable_ship_volume'],
             'rnt': data['office_rental_cost'],
             'at': updated_at,
             }
        )

    def select_universe_station(self, id):
        row = self.db.select_one_row(
            "SELECT ets_type_id,ets_name,ets_owner_id,ets_race_id,ets_x,ets_y,ets_z,ets_system_id,"
            " ets_reprocessing_efficiency,ets_reprocessing_stations_take,ets_max_dockable_ship_volume,"
            " ets_office_rental_cost,ets_updated_at "
            "FROM esi_tranquility_stations "
            "WHERE ets_station_id=%s;",
            id
        )
        if row is None:
            return None, None
        data = {
            'station_id': id,
            'type_id': row[0],
            'name': row[1],
            'position': {'x': row[4], 'y': row[5], 'z': row[6]},
            'system_id': row[7],
            'reprocessing_efficiency': row[8],
            'reprocessing_stations_take': row[9],
            'max_dockable_ship_volume': row[10],
            'office_rental_cost': row[11],
        }
        if row[2]:
            data.update({'owner': row[2]})
        if row[3]:
            data.update({'race_id': row[3]})
        return data, row[12]

    # -------------------------------------------------------------------------
    # universe/structures/
    # -------------------------------------------------------------------------

    def is_exist_structure_id(self, id):
        return self.is_exist_something(id, 'esi_universe_structures', 'eus_structure_id')

    def get_exist_universe_structure_ids(self):
        return self.get_exist_ids('esi_universe_structures', 'eus_structure_id', 'eus_updated_at')

    def get_absent_universe_structure_ids(self, ids):
        return self.get_absent_ids(ids, 'esi_universe_structures', 'eus_structure_id')

    def insert_or_update_universe_structure(self, id, data, forbidden, updated_at):
        """ inserts universe structure data into database

        :param id: unique structure id
        :param data: universe structure data
        :param updated_at: :class:`datetime.datetime`
        """
        # { "name": "Autama - Gunzey",
        #   "owner_id": 98285679,
        #   "position": {
        #    "x": 326015809896.0,
        #    "y": -3436537338.0,
        #    "z": 149013093495.0
        #   },
        #   "solar_system_id": 30001411,
        #   "type_id": 35825
        #  }
        if not forbidden:
            self.db.execute(
                "INSERT INTO esi_universe_structures("
                " eus_structure_id,"
                " eus_name,"
                " eus_owner_id,"
                " eus_system_id,"
                " eus_type_id,"
                " eus_x,eus_y,eus_z,"
                " eus_forbidden,"
                " eus_created_at,"
                " eus_updated_at) "
                "VALUES ("
                " %(id)s,"
                " %(nm)s,"
                " %(own)s,"
                " %(ss)s,"
                " %(ty)s,"
                " %(x)s,%(y)s,%(z)s,"
                " %(fbd)s,"
                " CURRENT_TIMESTAMP AT TIME ZONE 'GMT',"
                " TIMESTAMP WITHOUT TIME ZONE %(at)s) "
                "ON CONFLICT ON CONSTRAINT pk_eus DO UPDATE SET"
                " eus_name=%(nm)s,"
                " eus_owner_id=%(own)s,"
                " eus_system_id=%(ss)s,"
                " eus_type_id=%(ty)s,"
                " eus_x=%(x)s,eus_y=%(y)s,eus_z=%(z)s,"
                " eus_forbidden=%(fbd)s,"
                " eus_updated_at=TIMESTAMP WITHOUT TIME ZONE %(at)s;",
                {'id': id,
                 'nm': data['name'],
                 'own': data['owner_id'],
                 'ss': data['solar_system_id'],
                 'ty': data.get('type_id', None),
                 'x': data['position']['x'],
                 'y': data['position']['y'],
                 'z': data['position']['z'],
                 'fbd': forbidden,
                 'at': updated_at,
                 }
            )
        else:
            self.db.execute(
                "INSERT INTO esi_universe_structures("
                " eus_structure_id,"
                " eus_name,"
                " eus_system_id,"
                " eus_x,eus_y,eus_z,"
                " eus_forbidden,"
                " eus_created_at,"
                " eus_updated_at) "
                "VALUES ("
                " %(id)s,"
                " 'Unknown Structure',"
                " 0,"
                " 0,0,0,"
                " true,"
                " CURRENT_TIMESTAMP AT TIME ZONE 'GMT',"
                " TIMESTAMP WITHOUT TIME ZONE %(at)s) "
                "ON CONFLICT ON CONSTRAINT pk_eus DO UPDATE SET"
                " eus_forbidden=true,"
                " eus_updated_at=TIMESTAMP WITHOUT TIME ZONE %(at)s;",
                {'id': id,
                 'at': updated_at,
                 }
            )

    def select_universe_structure(self, id):
        row = self.db.select_one_row(
            "SELECT eus_name,eus_owner_id,eus_system_id,eus_type_id,eus_x,eus_y,eus_z,eus_forbidden,"
            " eus_updated_at "
            "FROM esi_universe_structures "
            "WHERE eus_structure_id=%s;",
            id
        )
        if row is None:
            return None, None
        data = {
            'name': row[0],
            'owner_id': row[1],
            'solar_system_id': row[2],
            'position': {'x': row[4], 'y': row[5], 'z': row[6]},
        }
        if row[3]:
            data.update({'type_id': row[3]})
        forbidden: bool = False if row[7] is None else bool(row[7])
        return data, forbidden, row[8]

    # -------------------------------------------------------------------------
    # corporations/{corporation_id}/structures/
    # -------------------------------------------------------------------------

    def is_exist_corporation_structure(self, id):
        return self.is_exist_something(id, 'esi_corporation_structures', 'ecs_structure_id')

    def get_absent_corporation_structure_ids(self, ids):
        return self.get_absent_ids(ids, 'esi_corporation_structures', 'ecs_structure_id')

    def insert_or_update_corporation_structure(self, data, updated_at):
        """ inserts corporation structure data into database

        :param data: corporation structure data
        """
        # { "corporation_id": 98150545,
        #   "fuel_expires": "2021-03-28T09:00:00Z",
        #   "profile_id": 78795,
        #   "reinforce_hour": 16,
        #   "services": [
        #    {
        #     "name": "Manufacturing (Standard)",
        #     "state": "online"
        #    }
        #   ],
        #   "state": "shield_vulnerable",
        #   "structure_id": 1035620655696,
        #   "system_id": 30000153,
        #   "type_id": 35825
        # }
        self.db.execute(
            "INSERT INTO esi_corporation_structures("
            " ecs_structure_id,"
            " ecs_corporation_id,"
            " ecs_type_id,"
            " ecs_system_id,"
            " ecs_profile_id,"
            " ecs_created_at,"
            " ecs_updated_at) "
            "VALUES ("
            " %(id)s,"
            " %(co)s,"
            " %(ty)s,"
            " %(ss)s,"
            " %(pr)s,"
            " CURRENT_TIMESTAMP AT TIME ZONE 'GMT',"
            " TIMESTAMP WITHOUT TIME ZONE %(at)s) "
            "ON CONFLICT ON CONSTRAINT pk_ecs DO UPDATE SET"
            " ecs_corporation_id=%(co)s,"  # могут ли структуры передаваться другим корпорациям?
            " ecs_profile_id=%(pr)s,"
            " ecs_updated_at=TIMESTAMP WITHOUT TIME ZONE %(at)s;",
            {'id': data['structure_id'],
             'co': data['corporation_id'],
             'ty': data['type_id'],
             'ss': data['system_id'],
             'pr': data['profile_id'],
             'at': updated_at,
             }
        )

    def get_exist_corporation_structures(self):
        rows = self.db.select_all_rows(
            "SELECT ecs_structure_id,ecs_corporation_id,ecs_type_id,ecs_system_id,ecs_profile_id,ecs_updated_at "
            "FROM esi_corporation_structures;"
        )
        if rows is None:
            return []
        data = []
        for row in rows:
            data.append({
                'structure_id': row[0],
                'corporation_id': row[1],
                'type_id': row[2],
                'system_id': row[3],
                'profile_id': row[4],
                'ext': {'updated_at': row[5]},
            })
        return data

    def mark_corporation_structures_updated(self, corporation_id, deleted_ids, updated_at):
        """ обновляет updated_at у существующих корп-структур и удаляет устаревшие (исчезнувшие) структуры

        :param corporation_id: corporation id to update its structure
        :param deleted_ids: obsolete corporation structure ids to remove from database
        :param updated_at: :class:`datetime.datetime`
        """
        if deleted_ids:
            self.db.execute(
                "DELETE FROM esi_corporation_structures "
                "WHERE ecs_structure_id IN (SELECT * FROM UNNEST(%s));",
                deleted_ids,
            )
        if updated_at:
            self.db.execute(
                "UPDATE esi_corporation_structures SET"
                " ecs_updated_at=TIMESTAMP WITHOUT TIME ZONE %(at)s "
                "WHERE ecs_corporation_id=%(id)s;",
                {'id': corporation_id,
                 'at': updated_at,
                 }
            )

    # -------------------------------------------------------------------------
    # corporations/{corporation_id}/assets/
    # -------------------------------------------------------------------------

    def clear_corporation_assets(self, corporation_id):
        """ delete corporation assets data from database
        """
        self.db.execute(
            "DELETE FROM esi_corporation_assets WHERE eca_corporation_id=%s;",
            corporation_id
        )

    def insert_or_update_corporation_assets(self, data, corporation_id, updated_at):
        """ inserts corporation assets data into database

        :param data: corporation assets data
        """
        # { "is_singleton": true,
        #   "item_id": 1035620655696,
        #   "location_flag": "AutoFit",
        #   "location_id": 30000153,
        #   "location_type": "solar_system",
        #   "quantity": 1,
        #   "type_id": 35825
        # }
        self.db.execute(
            "INSERT INTO esi_corporation_assets("
            " eca_item_id,"
            " eca_corporation_id,"
            " eca_type_id,"
            " eca_quantity,"
            " eca_location_id,"
            " eca_location_type,"
            " eca_location_flag,"
            " eca_is_singleton,"
            " eca_name,"
            " eca_created_at,"
            " eca_updated_at) "
            "VALUES ("
            " %(id)s,"
            " %(co)s,"
            " %(ty)s,"
            " %(q)s,"
            " %(loc)s,"
            " %(lty)s,"
            " %(lfl)s,"
            " %(sn)s,"
            " %(nm)s,"
            " CURRENT_TIMESTAMP AT TIME ZONE 'GMT',"
            " TIMESTAMP WITHOUT TIME ZONE %(at)s) "
            "ON CONFLICT ON CONSTRAINT pk_eca DO UPDATE SET"
            " eca_corporation_id=%(co)s,"  # ассеты могут перемещаться до того, как будет выяснено куда?
            " eca_quantity=%(q)s,"
            " eca_location_id=%(loc)s,"
            " eca_location_type=%(lty)s,"
            " eca_location_flag=%(lfl)s,"
            " eca_is_singleton=%(sn)s,"
            " eca_name=%(nm)s,"
            " eca_updated_at=TIMESTAMP WITHOUT TIME ZONE %(at)s;",
            {'id': data['item_id'],
             'co': corporation_id,
             'ty': data['type_id'],
             'q': data['quantity'],
             'loc': data['location_id'],
             'lty': data['location_type'],
             'lfl': data['location_flag'],
             'sn': data['is_singleton'],
             'nm': data.get('name', None),
             'at': updated_at,
             }
        )

    def get_exist_corporation_assets(self):
        rows = self.db.select_all_rows(
            "SELECT"
            " eca_item_id,"
            " eca_corporation_id,"
            " eca_type_id,"
            " eca_quantity,"
            " eca_location_id,"
            " eca_location_type,"
            " eca_location_flag,"
            " eca_is_singleton,"
            " eca_name,"
            " eca_updated_at "
            "FROM esi_corporation_assets;"
        )
        if rows is None:
            return []
        data = []
        for row in rows:
            ext = {'updated_at': row[9], 'corporation_id': row[1]}
            if row[8]:
                ext.update({'name': row[8]})
            data.append({
                'item_id': row[0],
                'type_id': row[2],
                'quantity': row[3],
                'location_id': row[4],
                'location_type': row[5],
                'location_flag': row[6],
                'is_singleton': row[7],
                'ext': ext,
            })
        return data

    def delete_obsolete_corporation_assets(self, deleted_ids):
        """ обновляет updated_at у существующих корп-ассетов и удаляет устаревшие (исчезнувшие) ассеты

        :param deleted_ids: obsolete corporation asset items ids to remove from database
        :param corporation_id: corporation id to update its assets
        :param updated_at: :class:`datetime.datetime`
        """
        if deleted_ids:
            self.db.execute(
                "DELETE FROM esi_corporation_assets "
                "WHERE eca_item_id IN (SELECT * FROM UNNEST(%s));",
                deleted_ids,
            )

    # -------------------------------------------------------------------------
    # corporations/{corporation_id}/blueprints/
    # -------------------------------------------------------------------------

    def clear_corporation_blueprints(self, corporation_id):
        """ delete corporation blueprints data from database
        """
        self.db.execute(
            "DELETE FROM esi_corporation_blueprints WHERE ecb_corporation_id=%s;",
            corporation_id
        )

    def insert_or_update_corporation_blueprints(self, data, corporation_id, updated_at):
        """ inserts corporation blueprints data into database

        :param data: corporation blueprints data
        """
        # { "item_id": 162478388,
        #   "location_flag": "CorpSAG4",
        #   "location_id": 1035318107573,
        #   "material_efficiency": 10,
        #   "quantity": -1,
        #   "runs": -1,
        #   "time_efficiency": 20,
        #   "type_id": 17860
        # }
        self.db.execute(
            "INSERT INTO esi_corporation_blueprints("
            " ecb_corporation_id,"
            " ecb_item_id,"
            " ecb_type_id,"
            " ecb_location_id,"
            " ecb_location_flag,"
            " ecb_quantity,"
            " ecb_time_efficiency,"
            " ecb_material_efficiency,"
            " ecb_runs,"
            " ecb_created_at,"
            " ecb_updated_at) "
            "VALUES ("
            " %(co)s,"
            " %(id)s,"
            " %(ty)s,"
            " %(loc)s,"
            " %(lfl)s,"
            " %(q)s,"
            " %(te)s,"
            " %(me)s,"
            " %(r)s,"
            " CURRENT_TIMESTAMP AT TIME ZONE 'GMT',"
            " TIMESTAMP WITHOUT TIME ZONE %(at)s) "
            "ON CONFLICT ON CONSTRAINT pk_ecb DO UPDATE SET"
            " ecb_corporation_id=%(co)s,"  # чертежи могут перемещаться до того, как будет выяснено куда?
            " ecb_type_id=%(ty)s,"
            " ecb_location_id=%(loc)s,"
            " ecb_location_flag=%(lfl)s,"
            " ecb_quantity=%(q)s,"
            " ecb_time_efficiency=%(te)s,"
            " ecb_material_efficiency=%(me)s,"
            " ecb_runs=%(r)s,"
            " ecb_updated_at=TIMESTAMP WITHOUT TIME ZONE %(at)s;",
            {'co': corporation_id,
             'id': data['item_id'],
             'ty': data['type_id'],
             'loc': data['location_id'],
             'lfl': data['location_flag'],
             'q': data['quantity'],
             'me': data['material_efficiency'],
             'te': data['time_efficiency'],
             'r': data['runs'],
             'at': updated_at,
             }
        )

    def get_exist_corporation_blueprints(self, corporation_id):
        rows = self.db.select_all_rows(
            "SELECT"
            " ecb_item_id,"
            " ecb_type_id,"
            " ecb_location_id,"
            " ecb_location_flag,"
            " ecb_quantity,"
            " ecb_time_efficiency,"
            " ecb_material_efficiency,"
            " ecb_runs,"
            " ecb_updated_at "
            "FROM esi_corporation_blueprints "
            "WHERE ecb_corporation_id=%s;",
            int(corporation_id),
        )
        if rows is None:
            return []
        data = []
        for row in rows:
            ext = {'updated_at': row[8], 'corporation_id': corporation_id}
            data.append({
                'item_id': row[0],
                'type_id': row[1],
                'location_id': row[2],
                'location_flag': row[3],
                'quantity': row[4],
                'time_efficiency': row[5],
                'material_efficiency': row[6],
                'runs': row[7],
                'ext': ext,
            })
        return data

    def delete_obsolete_corporation_blueprints(self, deleted_ids):
        """ обновляет updated_at у существующих корп-чертежей и удаляет устаревшие (исчезнувшие) БП

        :param deleted_ids: obsolete corporation blueprint items ids to remove from database
        :param corporation_id: corporation id to update its blueprints
        :param updated_at: :class:`datetime.datetime`
        """
        if deleted_ids:
            self.db.execute(
                "DELETE FROM esi_corporation_blueprints "
                "WHERE ecb_item_id IN (SELECT * FROM UNNEST(%s));",
                deleted_ids,
            )

    # -------------------------------------------------------------------------
    # corporations/{corporation_id}/industry/jobs/
    # -------------------------------------------------------------------------

    def insert_or_update_corporation_industry_jobs(self, data, corporation_id, updated_at):
        """ inserts corporation industry job data into database

        :param data: corporation industry job data
        """
        # print("INSERT {} {} {}".format(data['job_id'], data['activity_id'], data['status']))
        # return
        # { "activity_id": 3,
        #   "blueprint_id": 1035690963115,
        #   "blueprint_location_id": 1035704750584,
        #   "blueprint_type_id": 12055,
        #   "cost": 319478.0,
        #   "duration": 617929,
        #   "end_date": "2021-03-24T21:42:07Z",
        #   "facility_id": 1035620697572,
        #   "installer_id": 2116252240,
        #   "job_id": 453460908,
        #   "licensed_runs": 60,
        #   "location_id": 1035620697572,
        #   "output_location_id": 1035704750584,
        #   "probability": 1.0,
        #   "product_type_id": 12055,
        #   "runs": 9,
        #   "start_date": "2021-03-17T18:03:18Z",
        #   "status": "active"
        # }
        self.db.execute(
            "INSERT INTO esi_corporation_industry_jobs("
            " ecj_corporation_id,"
            " ecj_job_id,"
            " ecj_installer_id,"
            " ecj_facility_id,"
            " ecj_location_id,"
            " ecj_activity_id,"
            " ecj_blueprint_id,"
            " ecj_blueprint_type_id,"
            " ecj_blueprint_location_id,"
            " ecj_output_location_id,"
            " ecj_runs,"
            " ecj_cost,"
            " ecj_licensed_runs,"
            " ecj_probability,"
            " ecj_product_type_id,"
            " ecj_status,"
            " ecj_duration,"
            " ecj_start_date,"
            " ecj_end_date,"
            " ecj_pause_date,"
            " ecj_completed_date,"
            " ecj_completed_character_id,"
            " ecj_successful_runs,"
            " ecj_created_at,"
            " ecj_updated_at) "
            "VALUES ("
            " %(co)s,"
            " %(id)s,"
            " %(who)s,"
            " %(fac)s,"
            " %(loc)s,"
            " %(a)s,"
            " %(bp)s,"
            " %(bty)s,"
            " %(bpl)s,"
            " %(out)s,"
            " %(r)s,"
            " %(c)s,"
            " %(lr)s,"
            " %(p)s,"
            " %(pty)s,"
            " %(s)s,"
            " %(d)s,"
            " %(sdt)s,"
            " %(edt)s,"
            " %(pdt)s,"
            " %(cdt)s,"
            " %(cwho)s,"
            " %(sr)s,"
            " CURRENT_TIMESTAMP AT TIME ZONE 'GMT',"
            " TIMESTAMP WITHOUT TIME ZONE %(at)s) "
            "ON CONFLICT ON CONSTRAINT pk_ecj DO UPDATE SET"
            " ecj_status=%(s)s,"
            " ecj_pause_date=%(pdt)s,"
            " ecj_completed_date=%(cdt)s,"
            " ecj_completed_character_id=%(cwho)s,"
            " ecj_successful_runs=%(sr)s,"
            " ecj_updated_at=TIMESTAMP WITHOUT TIME ZONE %(at)s;",
            {'co': corporation_id,
             'id': data['job_id'],
             'who': data['installer_id'],
             'fac': data['facility_id'],
             'loc': data['location_id'],
             'a': data['activity_id'],
             'bp': data['blueprint_id'],
             'bty': data['blueprint_type_id'],
             'bpl': data['blueprint_location_id'],
             'out': data['output_location_id'],
             'r': data['runs'],
             'c': data.get('cost', None),
             'lr': data.get('licensed_runs', None),
             'p': data.get('probability', None),
             'pty': data.get('product_type_id', None),
             's': data['status'],
             'd': data['duration'],
             'sdt': data['start_date'],
             'edt': data['end_date'],
             'pdt': data.get('pause_date', None),
             'cdt': data.get('completed_date', None),
             'cwho': data.get('completed_character_id', None),
             'sr': data.get('successful_runs', None),
             'at': updated_at,
             }
        )

    def get_exist_corporation_industry_jobs(self, corporation_id: int, oldest_delivered_job=None):
        if oldest_delivered_job:
            where = "ecj_corporation_id={co} AND " \
                    "(ecj_completed_date IS NULL OR (" \
                    " ecj_status in ('delivered','cancelled') AND ecj_job_id>={job})" \
                    ")".\
                    format(co=corporation_id, job=oldest_delivered_job)
        else:
            where = "ecj_corporation_id={co} AND ecj_completed_date IS NULL".\
                    format(co=corporation_id)
        rows = self.db.select_all_rows(
            "SELECT"
            " ecj_corporation_id,"
            " ecj_job_id,"
            " ecj_installer_id,"
            " ecj_facility_id,"
            " ecj_location_id,"
            " ecj_activity_id,"
            " ecj_blueprint_id,"
            " ecj_blueprint_type_id,"
            " ecj_blueprint_location_id,"
            " ecj_output_location_id,"
            " ecj_runs,"
            " ecj_cost,"
            " ecj_licensed_runs,"
            " ecj_probability,"
            " ecj_product_type_id,"
            " ecj_status,"
            " ecj_duration,"
            " ecj_start_date,"
            " ecj_end_date,"
            " ecj_pause_date,"
            " ecj_completed_date,"
            " ecj_completed_character_id,"
            " ecj_successful_runs,"
            " ecj_updated_at "
            "FROM esi_corporation_industry_jobs "
            "WHERE {};".
            format(where)
        )
        if rows is None:
            return []
        data = []
        for row in rows:
            ext = {'updated_at': row[23], 'corporation_id': row[0]}
            data_item = {
                'job_id': row[1],
                'installer_id': row[2],
                'facility_id': row[3],
                'location_id': row[4],
                'activity_id': row[5],
                'blueprint_id': row[6],
                'blueprint_type_id': row[7],
                'blueprint_location_id': row[8],
                'output_location_id': row[9],
                'runs': row[10],
                'cost': row[11],
                'status': row[15],
                'duration': row[16],
                'start_date': row[17],
                'end_date': row[18],
                'ext': ext,
            }
            if row[12]:
                data_item.update({'licensed_runs': row[12]})
            if row[13]:
                data_item.update({'probability': row[13]})
            if row[14]:
                data_item.update({'product_type_id': row[14]})
            if row[19]:
                data_item.update({'pause_date': row[19]})
            if row[20]:
                data_item.update({'completed_date': row[20]})
            if row[21]:
                data_item.update({'completed_character_id': row[21]})
            if row[22]:
                data_item.update({'successful_runs': row[22]})
            data.append(data_item)
        return data

    # -------------------------------------------------------------------------
    # corporations/{corporation_id}/blueprints/
    # corporations/{corporation_id}/industry/jobs/
    # -------------------------------------------------------------------------

    def link_blueprint_copies_with_jobs(self):
        # настройки работы метода
        #  * deffered: время, после которого история не анализируется
        #  * missed: ждём кол-во часом не менее чем, чтобы дождаться когда будут добыты все недостающие данные
        missed_hours: int = 2
        deffered_hours: int = 24
        # формируем интервал анализа несвязанных чертежей и работ (ждём 2 часа, игнорируем слишком старые)
        where_hours: str = "((current_timestamp at time zone 'GMT' - interval '{mh} hours') >= ebc_created_at and " \
                           "ebc_created_at >= (current_timestamp at time zone 'GMT' - interval '{dh} hours'))".\
                           format(mh=missed_hours, dh=deffered_hours)

        # список продуктов, которые пока что являются не связанными в базе данных
        unlinked_blueprint_types = self.db.select_all_rows(
            "SELECT"
            " DISTINCT ebc_job_product_type_id "
            # debug: " ,(select sden_name from eve_sde_names"
            # debug: "  where sden_category=1 and sden_id=ebc_job_product_type_id) as type_name "
            "FROM esi_blueprint_costs "
            "WHERE"
            " ebc_job_activity=5 AND"  # copies
            " ebc_blueprint_id IS NULL AND"
            " ebc_transaction_type='f' AND"
            " {wh};".format(wh=where_hours)
        )

        for ubtype in unlinked_blueprint_types:
            type_id: int = int(ubtype[0])
            # debug: print(type_id, ubtype[1] if len(ubtype) == 2 else '')

            unlinked_bpcs_and_jobs = self.db.select_all_rows(
                "SELECT"
                " ebc_system_id as solar_system,"                                        # 0 *
                # " (select sden_name from eve_sde_names"
                # "  where sden_category=3 and sden_id=ebc_system_id) as solar_system,"  # 0 (debug only)
                " ebc_id as id,"                           # 1 *
                " ebc_blueprint_id as bpc_id,"             # 2 *
                # " ebc_blueprint_type_id as bpo_type,"
                " ebc_blueprint_runs as bp_runs,"          # 3 *
                " ebc_time_efficiency as te,"              # 4 *
                " ebc_material_efficiency as me,"          # 5 *
                # " ebc_job_id as job_id,"
                " ecj_blueprint_id as job_bp,"             # 6 *
                # " ebc_job_product_type_id as bpc_type,"
                " ebc_job_runs as rest_runs,"              # 7 * (меняется в процессе поиска чертежей)
                " ebc_job_time_efficiency as job_te,"      # 8 *
                " ebc_job_material_efficiency as job_me "  # 9 *
                "FROM"
                " esi_blueprint_costs"
                "  LEFT OUTER JOIN esi_corporation_industry_jobs ON (ebc_job_id=ecj_job_id) "
                "WHERE"
                " {wh} AND"
                " ((ebc_job_product_type_id=%(bty)s AND ebc_transaction_type='f' AND ebc_job_activity=5) OR"
                "  (ebc_blueprint_type_id=%(bty)s AND ebc_transaction_type='A' AND ebc_job_id IS NULL)"
                " )"
                "ORDER BY 2 DESC;".format(wh=where_hours),
                {'bty': type_id,
                 }
            )
            # debug: for unlinked in unlinked_bpcs_and_jobs:
            # debug:     print(unlinked)
            unlinked_jobs = [j for j in unlinked_bpcs_and_jobs if j[2] is None]

            # debug: print('unlinked_jobs', unlinked_jobs)
            used_ebc_ids = []
            for job in unlinked_jobs:
                solar_system = job[0]
                licensed_runs: int = job[3]
                blueprint_id: int = job[6]
                job_runs: int = job[7]
                te: int = job[8]
                me: int = job[9]
                found_ebc_ids = []
                for bpc in unlinked_bpcs_and_jobs:
                    if bpc[1] in used_ebc_ids:
                        continue
                    blueprint_copy_id: int = bpc[2]
                    # в списке имеются и работы и чертежи, пропускаем работы (ищем только чертежи)
                    if blueprint_copy_id is None:
                        continue
                    # если в список попал чертёж, который использовался в работе - он точно не её результат
                    if blueprint_id == blueprint_copy_id:
                        continue
                    # пропускаем те чертежи, которые сделаны в других солнечных системах
                    if bpc[0] == solar_system:
                        # пропускаем те чертежи, параметры которых отличаются от параметров работы
                        if (bpc[3] != licensed_runs) or (bpc[4] != te) or (bpc[5] != me):
                            continue
                        # debug: print("!!!!!!!! (", job_runs, ") : ", job[1], " -> ", blueprint_copy_id)
                        found_ebc_ids.append(bpc[1])
                        # как только найдено достаточное кол-во чертежей по этой работе, то прекращаем их поиск
                        job_runs -= 1
                        if job_runs == 0:
                            break
                # изменение связей в БД
                if found_ebc_ids:
                    self.db.execute(
                        "UPDATE esi_blueprint_costs SET("
                        " ebc_job_id,"
                        " ebc_job_corporation_id,"
                        " ebc_job_activity,"
                        " ebc_job_product_type_id,"
                        " ebc_industry_payment,"
                        " ebc_tax,"
                        " ebc_updated_at)="
                        "(SELECT"
                        "  ebc_job_id,"
                        "  ebc_job_corporation_id,"
                        "  ebc_job_activity,"
                        "  ebc_job_product_type_id,"
                        "  ebc_industry_payment,"
                        "  ebc_tax,"
                        "  CURRENT_TIMESTAMP AT TIME ZONE 'GMT'"
                        " FROM"
                        "  esi_blueprint_costs"
                        " WHERE"
                        "  ebc_id=%(jid)s"
                        ")"
                        "WHERE"
                        " ebc_id IN (SELECT * FROM UNNEST(%(ids)s));",
                        {'jid': job[1],
                         'ids': found_ebc_ids,
                         }
                    )
                    if job_runs == 0:
                        self.db.execute(
                            "UPDATE esi_blueprint_costs SET"
                            " ebc_job_runs=0,"
                            " ebc_transaction_type='p',"
                            " ebc_updated_at=CURRENT_TIMESTAMP AT TIME ZONE 'GMT' "
                            "WHERE ebc_id=%(jid)s;",
                            {'jid': job[1],
                             }
                        )
                    else:
                        self.db.execute(
                            "UPDATE esi_blueprint_costs SET"
                            " ebc_job_runs=%(r)s,"
                            " ebc_updated_at=CURRENT_TIMESTAMP AT TIME ZONE 'GMT' "
                            "WHERE ebc_id=%(jid)s;",
                            {'jid': job[1],
                             'r': job_runs,
                             }
                        )
                    used_ebc_ids += found_ebc_ids
            del used_ebc_ids

        del unlinked_blueprint_types

    def link_blueprint_invents_with_jobs(self):
        # настройки работы метода
        #  * deffered: время, после которого история не анализируется
        #  * missed: ждём кол-во часом не менее чем, чтобы дождаться когда будут добыты все недостающие данные
        missed_hours: int = 2
        deffered_hours: int = 24
        # формируем интервал анализа несвязанных чертежей и работ (ждём 2 часа, игнорируем слишком старые)
        where_hours: str = "((current_timestamp at time zone 'GMT' - interval '{mh} hours') >= ebc_created_at and " \
                           "ebc_created_at >= (current_timestamp at time zone 'GMT' - interval '{dh} hours'))".\
                           format(mh=missed_hours, dh=deffered_hours)

        # список продуктов, которые пока что являются не связанными в базе данных
        unlinked_blueprint_types = self.db.select_all_rows(
            "SELECT"
            " DISTINCT ebc_job_product_type_id "
            # debug: " ,(select sden_name from eve_sde_names"
            # debug: "  where sden_category=1 and sden_id=ebc_job_product_type_id) as type_name "
            "FROM esi_blueprint_costs "
            "WHERE"
            " ebc_job_activity=8 AND"  # invent
            " ebc_blueprint_id IS NULL AND"
            " ebc_transaction_type='f' AND"
            " ebc_job_successful_runs>0 AND"
            " {wh};".format(wh=where_hours)
        )

        for ubtype in unlinked_blueprint_types:
            type_id: int = int(ubtype[0])
            # debug: print(type_id, ubtype[1] if len(ubtype) == 2 else '')

            unlinked_bp2s_and_jobs = self.db.select_all_rows(
                "SELECT"
                " ebc_system_id,"                                                        # 0 *
                # " (select sden_name from eve_sde_names"
                # "  where sden_category=3 and sden_id=ebc_system_id) as solar_system,"  # 0 (debug only)
                " ebc_id,"                                 # 1 *
                " ebc_blueprint_id,"                       # 2 *
                " ebc_job_successful_runs "                # 3 * (меняется в процессе поиска чертежей)
                "FROM"
                " esi_blueprint_costs "
                "WHERE"
                " {wh} AND"
                " ((ebc_job_product_type_id=%(bty)s AND ebc_transaction_type='f' AND ebc_job_activity=8) OR"
                "  (ebc_blueprint_type_id=%(bty)s AND ebc_transaction_type='A' AND ebc_job_id IS NULL)"
                " )"
                "ORDER BY 2 DESC;".format(wh=where_hours),
                {'bty': type_id,
                 }
            )
            # debug: for unlinked in unlinked_bp2s_and_jobs:
            # debug:     print(unlinked)
            unlinked_jobs = [j for j in unlinked_bp2s_and_jobs if j[2] is None]

            # debug: print('unlinked_jobs', unlinked_jobs)
            used_ebc_ids = []
            for job in unlinked_jobs:
                solar_system = job[0]
                successful_runs: int = job[3]
                found_ebc_ids = []
                if successful_runs > 0:
                    for bpc in unlinked_bp2s_and_jobs:
                        if bpc[1] in used_ebc_ids:
                            continue
                        blueprint_t2_id: int = bpc[2]
                        # в списке имеются и работы и чертежи, пропускаем работы (ищем только чертежи)
                        if blueprint_t2_id is None:
                            continue
                        # пропускаем те чертежи, которые сделаны в других солнечных системах
                        if bpc[0] == solar_system:
                            # debug: print("!!!!!!!! (", successful_runs, ") : ", job[1], " -> ", job)
                            found_ebc_ids.append(bpc[1])
                            # как только найдено достаточное кол-во чертежей по этой работе, то прекращаем их поиск
                            successful_runs -= 1
                            if successful_runs == 0:
                                break
                    # изменение связей в БД
                    # debug: print('job_ebc_id', job[1], 'found_ebc_ids', found_ebc_ids)
                    if found_ebc_ids:
                        self.db.execute(
                            "UPDATE esi_blueprint_costs SET("
                            " ebc_job_id,"
                            " ebc_job_corporation_id,"
                            " ebc_job_activity,"
                            " ebc_job_product_type_id,"
                            " ebc_industry_payment,"
                            " ebc_tax,"
                            " ebc_updated_at)="
                            "(SELECT"
                            "  ebc_job_id,"
                            "  ebc_job_corporation_id,"
                            "  ebc_job_activity,"
                            "  ebc_job_product_type_id,"
                            "  ebc_industry_payment,"
                            "  ebc_tax,"
                            "  CURRENT_TIMESTAMP AT TIME ZONE 'GMT'"
                            " FROM"
                            "  esi_blueprint_costs"
                            " WHERE"
                            "  ebc_id=%(jid)s"
                            ")"
                            "WHERE"
                            " ebc_id IN (SELECT * FROM UNNEST(%(ids)s));",
                            {'jid': job[1],
                             'ids': found_ebc_ids,
                             }
                        )
                        if successful_runs == 0:
                            self.db.execute(
                                "UPDATE esi_blueprint_costs SET"
                                " ebc_job_successful_runs=0,"
                                " ebc_transaction_type='p',"
                                " ebc_updated_at=CURRENT_TIMESTAMP AT TIME ZONE 'GMT' "
                                "WHERE ebc_id=%(jid)s;",
                                {'jid': job[1],
                                 }
                            )
                        else:
                            self.db.execute(
                                "UPDATE esi_blueprint_costs SET"
                                " ebc_job_successful_runs=%(sr)s,"
                                " ebc_updated_at=CURRENT_TIMESTAMP AT TIME ZONE 'GMT' "
                                "WHERE ebc_id=%(jid)s;",
                                {'jid': job[1],
                                 'sr': successful_runs,
                                 }
                            )
                        used_ebc_ids += found_ebc_ids
            del used_ebc_ids

        del unlinked_blueprint_types
