from odoo import models, fields, api, _
from odoo.exceptions import AccessError


class ArchitecturalRequest(models.Model):
    _name = 'architectural.request'
    _inherit = ['mail.thread', 'mail.activity.mixin', 'portal.mixin']
    _description = 'Architectural Request'

    name = fields.Char(string='Subject')
    notes = fields.Html(string='Notes', help='Description of the type.')
    unit_id = fields.Many2one('res.partner', string='Unit', domain=[('is_unit', '=', True)])
    state = fields.Selection([
        ('new', 'New'),
        ('review', 'In-review'),
        ('approved', 'Approved'),
        ('declined', 'Declined'),
    ], string='Status', index=True, copy=False, required=True,default='new', track_visibility='onchange')
    attachment_ids = fields.Many2many(
        'ir.attachment', 'architectural_request_attachment_rel',
        'architecture_id', 'attachment_id',
        string='Attachments',
        help='Attachments are linked to a document through model / res_id and to the request '
             'through this field.')

    def _compute_portal_url(self):
        super(ArchitecturalRequest, self)._compute_portal_url()
        for order in self:
            order.portal_url = '/my/architectural/requests/%s' % (order.id)

    def get_mail_url(self):
        return self.get_share_url()

    @api.multi
    def get_access_action(self, access_uid=None):
        """ Instead of the classic form view, redirect to the online order for
        portal users or if force_website=True in the context. """
        # TDE note: read access on sales order to portal users granted to followed sales orders
        self.ensure_one()
        user, record = self.env.user, self
        if access_uid:
            user = self.env['res.users'].sudo().browse(access_uid)
            record = self.sudo(user)
        if user.share or self.env.context.get('force_website'):
            try:
                record.check_access_rule('read')
            except AccessError:
                if self.env.context.get('force_website'):
                    return {
                        'type': 'ir.actions.act_url',
                        'url': '/my/architectural/requests/%s' % self.id,
                        'target': 'self',
                        'res_id': self.id,
                    }
                else:
                    pass
            else:
                return {
                    'type': 'ir.actions.act_url',
                    'url': '/my/architectural/requests/%s?access_token=%s' % (self.id, self.access_token),
                    'target': 'self',
                    'res_id': self.id,
                }
        return super(ArchitecturalRequest, self).get_access_action(access_uid)
