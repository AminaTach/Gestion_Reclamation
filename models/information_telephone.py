from odoo import models, fields, api

class InformationTelephone(models.Model):
    _name = 'information.telephone'
    _description = 'Informations Supplémentaires Téléphoniques'

    name = fields.Char(string="Titre", required=True, help="Titre ou sujet de l'information.")
    description = fields.Text(string="Description", help="Détails de l'information récupérée.")
    contact_date = fields.Datetime(string="Date de Contact", default=fields.Datetime.now, help="Date et heure du contact téléphonique.")
    phone_number = fields.Char(string="Numéro de Téléphone", help="Numéro de téléphone utilisé pour le contact.")
    reclamation_id = fields.Many2one('gestion.reclamation', string="Réclamation Associée", help="Réclamation liée à cette information.")
    user_id = fields.Many2one('res.users', string="Utilisateur", default=lambda self: self.env.user, help="Utilisateur ayant saisi l'information.")
