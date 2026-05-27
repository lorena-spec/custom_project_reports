{
    'name': 'Custom Project Reports - Cierre de Proyectos',
    'version': '14.0.1.0.0',
    'category': 'Project',
    'summary': 'Reportes personalizados para cierre de proyectos con análisis de costos',
    'author': 'PATHPROFIT S.A.',
    'license': 'LGPL-3',
    'depends': [
        'project',
        'analytic',
        'mail',
    ],
    'data': [
        'security/ir.model.access.csv',
        'reports/project_closure_report.xml',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
}
