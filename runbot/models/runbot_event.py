import logging

from odoo import api, fields, models

_logger = logging.getLogger(__name__)


class RunbotEvent(models.Model):
    _inherit = 'ir.logging'

    TYPES = [
        (t, t.capitalize()) for t in 'client server runbot'.split()
    ]

    build_id = fields.Many2one('runbot.build',
                               string='Build',
                               index=True,
                               ondelete='cascade')

    type = fields.Selection(TYPES,
                            string='Type',
                            required=True,
                            index=True)

    @api.model_cr
    def init(self):
        super(RunbotEvent, self).init()
        self._cr.execute("""
CREATE OR REPLACE FUNCTION runbot_set_logging_build() RETURNS TRIGGER AS $$
BEGIN
  IF (new.build_id IS NULL AND new.dbname IS NOT NULL AND new.dbname != current_database()) THEN
    UPDATE ir_logging l
       SET build_id = split_part(new.dbname, '-', 1)::integer
     WHERE l.id = new.id;
  END IF;
RETURN NULL;
END;
$$ language plpgsql;

DO $$
BEGIN
    CREATE TRIGGER runbot_new_logging
    AFTER INSERT ON ir_logging
    FOR EACH ROW
    EXECUTE PROCEDURE runbot_set_logging_build();
EXCEPTION
    WHEN duplicate_object THEN
END;
$$;
        """)  # noqa: E501
