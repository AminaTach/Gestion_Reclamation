# gestion_reclamations/models/reclamation.py
from odoo import models, fields, api

class Reclamation(models.Model):
    _name = 'gestion.reclamation'
    _description = 'Réclamation'

    # Champs de base
    name = fields.Char(string="Identifiant", required=True, default="Nouvelle Réclamation", readonly=True)
    date = fields.Date(string="Date", default=fields.Date.today, required=True)
    objet = fields.Char(string="Objet de la réclamation", required=True)
    description = fields.Text(string="Description")

    # Relation avec le modèle 'res.partner' (contact)
    reclamant_id = fields.Many2one('res.partner', string="Réclamant", required=True)

    # Champ pour les documents justificatifs (One2many field)
    document_ids = fields.One2many('ir.attachment', 'res_id', string="Documents justificatifs", domain=[('res_model', '=', 'gestion.reclamation')])

    # Champ pour l'agence (à renseigner automatiquement)
    agence_id = fields.Many2one('res.partner', string="Agence", default=lambda self: self.env.user.partner_id.id)

    # Champ booléen pour indiquer si la réclamation est urgente
    urgent = fields.Boolean(string="Urgent")

    # Champ de sélection pour le type de réclamation
    type_reclamation = fields.Selection([
        ('technique', 'Technique'),
        ('commercial', 'Commercial'),
    ], string="Type de réclamation", required=True)

    # Champ de sélection pour l'origine de la réclamation
    origine_reclamation = fields.Selection([
        ('citoyen', 'Citoyen'),
        ('entreprise', 'Entreprise'),
        ('cellule_veille', 'Cellule Veille'),
    ], string="Origine de la réclamation", required=True)

     # Override the create method to generate a unique identifier
    @api.model
    def create(self, vals):
        if vals.get('name', 'Nouvelle Réclamation') == 'Nouvelle Réclamation':
            sequence = self.env['ir.sequence'].next_by_code('gestion.reclamation') or 'Nouvelle Réclamation'
            vals['name'] = sequence
        return super(Reclamation, self).create(vals)