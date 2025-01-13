# gestion_reclamations/models/reclamation.py
from odoo import models, fields, api


class ProjectTask(models.Model):
    _inherit = 'project.task'

    # Ajouter un champ Many2many pour les employés assignés
    equipe_intervention_ids = fields.Many2many(
        'hr.employee',  # Modèle lié
        string="Équipe d'Intervention",  # Libellé du champ
        help="Sélectionnez les employés assignés à cette tâche."
    )

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

    etat_reclamation = fields.Selection([
        ('en attente', 'En attente'),
        ('en cours de traitement', 'En cours de traitement'),
        ('traitee', 'Traitee'),
        ('archivee', 'Archivée'),
    ], string="Etat de réclamation", required=True, default = "en attente")

    # Champ de sélection pour l'origine de la réclamation
    origine_reclamation = fields.Selection([
        ('citoyen', 'Citoyen'),
        ('entreprise', 'Entreprise'),
        ('cellule_veille', 'Cellule Veille'),
    ], string="Origine de la réclamation", required=True)

    archived = fields.Boolean(string="Archivé", default=False)  # Add this line
    equipe_intervention_ids = fields.Many2many(
        'hr.employee',  # Modèle lié
        string="Équipe d'Intervention",  # Libellé du champ
        help="Sélectionnez les employés assignés à cette réclamation."
    )  # Équipe d'intervention

    date_limite = fields.Date(string="Date Limite", required=True)  # Date limite pour traiter la réclamation
    task_id = fields.Many2one('project.task', string="Tâche Associée")  # Tâche associée

    def creer_tache(self):
        for rec in self:
            if not rec.task_id:  # Vérifier qu'une tâche n'existe pas déjà
                # Créer un projet s'il n'existe pas déjà
                projet = self.env['project.project'].search([('name', '=', 'Projet de Gestion des Réclamations')], limit=1)
                if not projet:
                    projet = self.env['project.project'].create({
                        'name': 'Projet de Gestion des Réclamations',
                        'user_id': self.env.user.id,  # Responsable du projet
                    })

                # Créer la tâche
                task = self.env['project.task'].create({
                    'name': f"Tâche pour la réclamation {rec.name}",
                    'project_id': projet.id,  # Utiliser le projet créé
                    'equipe_intervention_ids': [(6, 0, rec.equipe_intervention_ids.ids)],  # Assigner les employés
                    'date_deadline': rec.date_limite,  # Date limite de la tâche
                    'description': rec.description,  # Description de la tâche
                })
                rec.task_id = task.id  # Associer la tâche à la réclamation
                rec.etat_reclamation = 'en cours de traitement'  # Mettre à jour l'état

    # Méthode pour automatiser la création de tâches lors du changement d'état
    def write(self, vals):
        if 'etat_reclamation' in vals and vals['etat_reclamation'] == 'en cours de traitement':
            self.creer_tache()  # Créer une tâche lorsque l'état change
        return super(Reclamation, self).write(vals)

    def archive_reclamation(self):
        """
        Archive la réclamation en changeant son état à 'archivee'.
        """
        for record in self:
            if record.etat_reclamation == 'traitee':
                record.write({'etat_reclamation': 'archivee', 'archived': True})
            else:
                raise models.ValidationError("Seules les réclamations traitées peuvent être archivées.")

     # Override the create method to generate a unique identifier
    @api.model
    def create(self, vals):
        if vals.get('name', 'Nouvelle Réclamation') == 'Nouvelle Réclamation':
            sequence = self.env['ir.sequence'].next_by_code('gestion.reclamation') or 'Nouvelle Réclamation'
            vals['name'] = sequence
        return super(Reclamation, self).create(vals)

