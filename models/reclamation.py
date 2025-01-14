# gestion_reclamations/models/reclamation.py
from odoo import models, fields, api
from odoo.exceptions import ValidationError
import base64
import logging

_logger = logging.getLogger(__name__)

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

    def action_send_receipt(self):
        try:
            # Vérifier que l'email du réclamant est défini
            if not self.reclamant_id.email:
                raise ValidationError("L'adresse email du réclamant n'est pas définie.")

            # Générer le PDF
            pdf_content = self._generate_pdf_content()

            # Créer un enregistrement d'attachment
            attachment = self.env['ir.attachment'].create({
                'name': f'Reçu de réclamation {self.name}.pdf',
                'type': 'binary',
                'datas': base64.b64encode(pdf_content),
                'res_model': self._name,
                'res_id': self.id,
            })

            # Récupérer le modèle de mail
            template = self.env.ref('Gestion_Reclamation.email_template_receipt')

            # Définir les adresses email
            template.email_from = self.env.user.email
            template.email_to = self.reclamant_id.email

            _logger.info(f"Envoi de l'email en cours...")
            _logger.info(f"Email FROM : {template.email_from}")
            _logger.info(f"Email TO : {template.email_to}")
            _logger.info(f"Attachment : {attachment.name}")

            # Envoyer l'email avec le template et la pièce jointe
            template.attachment_ids = [(6, 0, [attachment.id])]
            template.send_mail(self.id, force_send=True)

            # Message de succès
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': 'Succès',
                    'message': 'Le reçu de réception a été envoyé avec succès.',
                    'type': 'success',
                    'sticky': False,
                }
            }
        except Exception as e:
            # Message d'erreur en cas d'échec
            _logger.error(f"Erreur lors de l'envoi du reçu : {str(e)}")
            raise ValidationError(f"Une erreur s'est produite lors de l'envoi du reçu : {str(e)}")

    def _generate_pdf_content(self):
        # Exemple de génération de contenu PDF (à adapter selon vos besoins)
        from io import BytesIO
        from reportlab.pdfgen import canvas
        from reportlab.lib.pagesizes import A4
        from reportlab.lib import colors
        from reportlab.lib.styles import getSampleStyleSheet
        from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer

        buffer = BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=A4)
        styles = getSampleStyleSheet()
 
        # Définir les styles
        title_style = styles['Title']
        heading_style = styles['Heading1']
        body_style = styles['BodyText']
        
        content = []

        # Titre
        title = Paragraph(f"Reçu de réclamation: {self.name}", title_style)
        content.append(title)
        content.append(Spacer(1, 12))

        # Date
        date = Paragraph(f"Date: {self.date}", heading_style)
        content.append(date)
        content.append(Spacer(1, 12))

        # Réclamant
        reclamant = Paragraph(f"Réclamant: {self.reclamant_id.name}", heading_style)
        content.append(reclamant)
        content.append(Spacer(1, 12))

        # Description
        description = Paragraph(f"Description: {self.description}", body_style)
        content.append(description)
        content.append(Spacer(1, 12))

        # Construire le PDF
        doc.build(content)

        pdf_content = buffer.getvalue()
        buffer.close()
        return pdf_content