from odoo import http
from odoo.http import request
import base64  # Import the base64 module
from datetime import datetime, timedelta

class ReclamationController(http.Controller):

    @http.route('/formulaire-de-reclamation', type='http', auth="public", website=True, csrf=False)
    def reclamation_form(self):
        """Affiche le formulaire de réclamation."""
        return request.render('Gestion_Reclamation.reclamation_form_page')

    @http.route('/reclamation/submit', type='http', auth="public", website=True, csrf=False)
    def submit_reclamation(self, **post):
        """Traite la soumission du formulaire de réclamation."""
        # Récupérer les données du formulaire
        name = post.get('name')
        prenom = post.get('prenom')
        phone = post.get('phone')
        email = post.get('email')
        objet = post.get('objet')
        description = post.get('description')
        documents_justificatifs = request.httprequest.files.getlist('documents_justificatifs')  

        # Créer ou mettre à jour le réclamant (res.partner)
        reclamant = request.env['res.partner'].sudo().search([('email', '=', email)], limit=1)
        if not reclamant:
            reclamant = request.env['res.partner'].sudo().create({
                'name': f"{name} {prenom}",  # Combine nom and prenom
                'email': email,
                'phone': phone,
            })
        else:
            reclamant.write({
                'name': f"{name} {prenom}",  # Update nom and prenom
                'phone': phone,  # Update phone number
            })

        # Créer la réclamation dans le modèle gestion.reclamation
        date_limite = (datetime.now() + timedelta(days=7)).date()  # Set to 7 days from today
        reclamation_sequence = request.env['ir.sequence'].next_by_code('gestion.reclamation')
        reclamation_name = f"#{reclamation_sequence}"
        reclamation = request.env['gestion.reclamation'].sudo().create({
            'name': reclamation_name,
            'objet': objet,
            'description': description,
            'reclamant_id': reclamant.id,
            # Les champs suivants sont définis par défaut ou automatiquement
            'urgent': False,  # Par défaut, non urgent
            'type_reclamation': 'technique',  # Par défaut, type technique
            'origine_reclamation': 'citoyen',  # Par défaut, origine citoyen
            'etat_reclamation': 'en attente',
            'date_limite': date_limite,
        })
        
        # Enregistrer les fichiers joints
        for file in documents_justificatifs:
            if file:
                file_data = base64.b64encode(file.read())
                request.env['custom.attachment'].sudo().create({
                    'name': file.filename,
                    'datas': file_data,
                    'res_id': reclamation.id,
                })
        
        # Rediriger l'utilisateur vers une page de confirmation
        return request.redirect('/reclamation/confirmation')

    @http.route('/reclamation/confirmation', type='http', auth="public", website=True)
    def reclamation_confirmation(self):
        """Affiche la page de confirmation."""
        return request.render('Gestion_Reclamation.reclamation_confirmation_page')