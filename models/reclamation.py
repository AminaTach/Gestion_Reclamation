# gestion_reclamations/models/reclamation.py
from odoo import models, fields, api

class Reclamation(models.Model):
    _name = 'gestion.reclamation'
    _description = 'Réclamation'

    # Champs de base
    name = fields.Char(string="Identifiant", required=True, default="Nouvelle Réclamation")
    date = fields.Date(string="Date", default=fields.Date.today, required=True)
    objet = fields.Char(string="Objet de la réclamation", required=True)
    description = fields.Text(string="Description")

    # Relation avec le modèle 'res.partner' (contact)
    reclamant_id = fields.Many2one('res.partner', string="Réclamant", required=True)

    # Champ pour les documents justificatifs
    documents_justificatifs = fields.Binary(string="Documents justificatifs")

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

    # Champ de l'etat de reclamation
    etat_reclamation = fields.Selection(
        [
            ('draft', 'Brouillon'),
            ('open', 'Ouverte'),
            ('resolved', 'Résolue'),
            ('closed', 'Fermée')
        ],
        string="État",
        default='draft',
        required=True,
    )

    # Champ pour les informations téléphoniques
    information_ids = fields.One2many(
        'information.telephone', 'reclamation_id', string="Informations Téléphoniques"
    )


    # Champ de l'employé responsable de la réclamation
    employee_id = fields.Many2one('hr.employee', string="Employé", help="Sélectionnez l'employé responsable de cette réclamation.")



    @api.model
    def create(self, vals):
        """Override create to send notification on creation."""
        res = super(GestionReclamation, self).create(vals)
        res._send_notification('create')
        return res

    @api.onchange('etat_reclamation')
    def _onchange_etat_reclamation(self):
        """Send notification when the state changes."""
        for record in self:
            record._send_notification('change')

    def _send_notification(self, event):
        """Send notification based on event."""
        message = ""
        if event == 'create':
            message = f"La réclamation '{self.name}' a été créée."
        elif event == 'change':
            message = f"L'état de la réclamation '{self.name}' est passé à '{dict(self._fields['etat_reclamation'].selection).get(self.etat_reclamation)}'."
        
        # Envoyer un e-mail
        self._send_email_notification(message)

        # Envoyer un SMS (utilisez une passerelle SMS, exemple fictif ici)
        # self._send_sms_notification(message)

    def _send_email_notification(self, message):
        """Send email notification."""
        mail_values = {
            'subject': 'Notification Réclamation',
            'body_html': f'<p>{message}</p>',
            'email_to': self.employee_id.work_email or 'admin@example.com',
        }
        self.env['mail.mail'].create(mail_values).send()

    def _send_sms_notification(self, message):
        """Send SMS notification (example implementation)."""
        sms_service = self.env['sms.service']
        if sms_service:
            sms_service.send_sms(
                number=self.employee_id.mobile_phone,
                message=message
            )