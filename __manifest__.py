# gestion_reclamations/__manifest__.py
{
    'name': 'Gestion des Réclamations',
    'version': '1.0',
    'summary': 'Module pour gérer les réclamations',
    'description': """
        Ce module permet de gérer les réclamations des clients.
        Il inclut des fonctionnalités pour suivre les réclamations, les documents justificatifs, et les informations du réclamant.
    """,
    'author': 'Equipe3',
    'category': 'Services',
<<<<<<< HEAD
    'depends': ['base', 'contacts', 'website'],
    'data': [
      'data/sequence.xml',
      'security/ir.model.access.csv',
      'views/reclamation_views.xml',
      'views/reclamation_templates.xml',
      'report/receipt_report.xml',
      'report/pv_decision.xml',
      'mail_template.xml'
=======
    'depends': ['base', 'contacts', 'hr', 'mail'],
    'data': [
        'security/ir.model.access.csv',
        'views/reclamation_views.xml',     
>>>>>>> bb3ddcfb97d365064683c195e3cb1286c8d5c4c6
    ],
    'demo': [
        'demo.xml',  # Ajoutez ce fichier pour les données de démonstration
    ],
    'installable': True,
    'application': True,
}