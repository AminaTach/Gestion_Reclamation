from odoo import models, fields, api

class Appel(models.Model):
    _name = 'gestion.appel'
    _description = 'Détails des Appels'

    name = fields.Char(string='Objet de l\'appel', required=True)
    date_appel = fields.Datetime(string='Date et Heure', required=True, default=fields.Datetime.now)
    duree = fields.Float(string='Durée (minutes)')
    description = fields.Text(string='Description')
    contact_id = fields.Many2one('res.partner', string='Contact', required=True)
    employee_id = fields.Many2one('hr.employee', string='Employé')
    statut = fields.Selection([
        ('prevu', 'Prévu'),
        ('effectue', 'Effectué'),
        ('annule', 'Annulé'),
    ], string='Statut', default='prevu')

    # Optionnel : Relation avec les réclamations
    reclamant_id = fields.Many2one('gestion.reclamation', string='Réclamation Associée')
