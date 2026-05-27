from odoo import models, fields, api
from datetime import datetime
import logging

_logger = logging.getLogger(__name__)

class ProjectProjectClosure(models.Model):
    _inherit = 'project.project'

    total_cost_planned = fields.Float(
        string="Costo Total Planificado",
        compute='_compute_closure_metrics',
        store=False,
    )
    total_cost_real = fields.Float(
        string="Costo Total Real",
        compute='_compute_closure_metrics',
        store=False,
    )
    cost_variance = fields.Float(
        string="Desviación de Costos",
        compute='_compute_closure_metrics',
        store=False,
    )
    cost_variance_pct = fields.Float(
        string="% Varianza de Costos",
        compute='_compute_closure_metrics',
        store=False,
    )
    closure_date = fields.Date(string="Fecha de Cierre")
    closure_notes = fields.Text(string="Notas de Cierre")

    @api.depends('analytic_account_id', 'analytic_account_id.line_ids')
    def _compute_closure_metrics(self):
        for project in self:
            total_planned = 0.0
            total_real = 0.0
            
            if project.analytic_account_id:
                analytic_lines = self.env['account.analytic.line'].search([
                    ('account_id', '=', project.analytic_account_id.id),
                ])
                
                for line in analytic_lines:
                    if line.amount < 0:
                        total_real += abs(line.amount)
                
                if project.analytic_account_id.amount_max:
                    total_planned = project.analytic_account_id.amount_max
            
            project.total_cost_planned = total_planned
            project.total_cost_real = total_real
            project.cost_variance = total_real - total_planned
            
            if total_planned > 0:
                project.cost_variance_pct = (project.cost_variance / total_planned) * 100
            else:
                project.cost_variance_pct = 0.0

    def action_generate_closure_report(self):
        return self.env.ref('custom_project_reports.action_report_project_closure').report_action(self)

    def action_close_project(self):
        for project in self:
            project.closure_date = fields.Date.today()
            _logger.info(f"Proyecto {project.name} cerrado el {fields.Date.today()}")

    def generate_closure_report_and_email(self):
        for project in self:
            try:
                report = self.env.ref('custom_project_reports.action_report_project_closure')
                pdf_content, pdf_type = report.render_qweb_pdf(project.ids)
                
                filename = f"Cierre_{project.name.replace('/', '-')}.pdf"
                attachment = self.env['ir.attachment'].create({
                    'name': filename,
                    'type': 'binary',
                    'datas': pdf_content,
                    'res_model': 'project.project',
                    'res_id': project.id,
                    'public': False,
                })
                
                _logger.info(f"PDF generado: {filename}")
                
                if project.user_id and project.user_id.email:
                    mail_values = {
                        'subject': f'Reporte de Cierre de Proyecto - {project.name}',
                        'body_html': f'''<p>Proyecto {project.name} ha sido cerrado.</p>''',
                        'email_from': self.env.user.email_formatted or 'noreply@example.com',
                        'email_to': project.user_id.email,
                        'attachment_ids': [(6, 0, [attachment.id])],
                    }
                    
                    mail_id = self.env['mail.mail'].create(mail_values)
                    mail_id.send()
                    _logger.info(f"Email enviado a {project.user_id.email}")
                
            except Exception as e:
                _logger.error(f"Error al generar reporte: {str(e)}")
