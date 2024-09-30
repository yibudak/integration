# Copyright 2024 Ahmet Yiğit Budak (https://github.com/yibudak)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from openupgradelib import openupgrade


def _convert_deci_type_to_char(env):
    openupgrade.logged_query(
        env.cr,
        """
        ALTER TABLE delivery_carrier
        ALTER COLUMN deci_type TYPE CHARACTER VARYING;
        """,
    )


@openupgrade.migrate()
def migrate(env, version):
    _convert_deci_type_to_char(env)
