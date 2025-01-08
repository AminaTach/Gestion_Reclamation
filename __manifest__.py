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
    'depends': ['base', 'contacts'],
    'data': [
        'security/ir.model.access.csv',
        'views/reclamation_views.xml',
    ],
    'demo': [
        'demo.xml',  # Ajoutez ce fichier pour les données de démonstration
    ],
    'installable': True,
    'application': True,
}