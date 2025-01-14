from odoo import models

class IrActionsReport(models.Model):
    _inherit = 'ir.actions.report'

    def _render_template(self, template, values):
        # Ajouter des messages de débogage
        print("DEBUG: _render_template called")  # Ce message devrait apparaître dans les logs
        values['object'] = self.env['gestion.reclamation'].browse(values.get('doc_ids'))
        self.env.cr.execute("SELECT 1")  # Force une requête SQL pour vérifier la connexion
        self.env.cr.fetchall()
        self.env.cr.execute("SELECT id FROM gestion_reclamation LIMIT 1")  # Vérifie que la table existe
        self.env.cr.fetchall()
        self.env.cr.execute("SELECT id FROM ir_ui_view WHERE name = 'report_receipt'")  # Vérifie que le template existe
        self.env.cr.fetchall()
        return super(IrActionsReport, self)._render_template(template, values)