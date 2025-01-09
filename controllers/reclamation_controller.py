from odoo import http
from odoo.http import request
import base64  # Import the base64 module

class ReclamationController(http.Controller):

    @http.route('/formulaire-de-reclamation', type='http', auth="public", website=True)
    def reclamation_form(self):
        """Affiche le formulaire de réclamation."""
        return request.render('Odoo_Gestion_Reclamation.reclamation_form_page')

    @http.route('/reclamation/submit', type='http', auth="public", website=True, csrf=False)
    def submit_reclamation(self, **post):
        """Traite la soumission du formulaire de réclamation."""
        # Récupérer les données du formulaire
        name = post.get('name')
        email = post.get('email')
        objet = post.get('objet')
        description = post.get('description')
        documents_justificatifs = request.httprequest.files.getlist('documents_justificatifs')  

        # Rechercher ou créer le réclamant (res.partner) à partir de l'email
        reclamant = request.env['res.partner'].sudo().search([('email', '=', email)], limit=1)
        if not reclamant:
            reclamant = request.env['res.partner'].sudo().create({
                'name': name,
                'email': email,
            })

        # Créer la réclamation dans le modèle gestion.reclamation
        reclamation = request.env['gestion.reclamation'].sudo().create({
            'name': name,
            'objet': objet,
            'description': description,
            'reclamant_id': reclamant.id,
            # Les champs suivants sont définis par défaut ou automatiquement
            'urgent': False,  # Par défaut, non urgent
            'type_reclamation': 'technique',  # Par défaut, type technique
            'origine_reclamation': 'citoyen',  # Par défaut, origine citoyen
        })
        # Enregistrer les fichiers joints
        for file in documents_justificatifs:
            if file:
                file_data = base64.b64encode(file.read())
                request.env['ir.attachment'].sudo().create({
                    'name': file.filename,
                    'datas': file_data,
                    'res_model': 'gestion.reclamation',
                    'res_id': reclamation.id,
                })

        # Rediriger l'utilisateur vers une page de confirmation
        return request.redirect('/reclamation/confirmation')