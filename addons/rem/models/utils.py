# -*- coding: utf-8 -*-


class RentDate(object):

    def __init__(self, env, years=0.0, months=0.0, weeks=0.0, days=0.0):
        # Quantities
        self.years = years
        self.months = months
        self.weeks = weeks
        self.days = days
        # Rent Rates
        self.r_years = years
        self.r_months = months
        self.r_weeks = weeks
        self.r_days = days
        # Descriptions
        self.t_months = False
        self.t_weeks = False
        self.t_days = False
        self.uom_day = env.ref('rem.product_rent_day')
        self.uom_week = env.ref('rem.product_rent_week')
        self.uom_month = env.ref('rem.product_rent_month')

    def __str__(self):
        str = ("Years=%s Months=%s Weeks=%s Days=%s" % (self.years, self.months, self.weeks, self.weeks))
        str += ("Year Rate=%s Month Rate=%s Week Rate=%s Day Rate=%s" % (self.r_years, self.r_months, self.r_weeks, self.r_weeks))
        return str

    def get_lines(self, product_id):
        res = []
        if self.months > 0:
            res.append({
                'name': self.t_months,
                'product_id': product_id,
                'qtt': self.months,
                'uom': self.uom_month.id,
                'price': self.r_months
            })

        if self.weeks > 0:
            res.append({
                'name': self.t_weeks,
                'product_id': product_id,
                'qtt': self.weeks,
                'uom': self.uom_week.id,
                'price': self.r_weeks
            })

        if self.days > 0:
            res.append({
                'name': self.t_days,
                'product_id': product_id,
                'qtt': self.days,
                'uom': self.uom_day.id,
                'price': self.r_days
            })
        return res