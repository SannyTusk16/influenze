from application.database import db


class Advertisement(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    niche_id = db.Column(db.Integer, db.ForeignKey('niche.niche_id'))
    campaign_id = db.Column(db.Integer, db.ForeignKey('campaign.campaign_id'))
    influencer_id = db.Column(db.Integer, db.ForeignKey('influencer.influencer_id'))
    status = db.Column(db.String(20))
    advertisement_name=db.Column(db.String(30))
    budget=db.Column(db.Integer)
    
    advertisement_niches=db.relationship('Niche',secondary='advertisement_niche_association',back_populates='niche_advertisements')
    advertisement_campaigns=db.relationship('Campaign',secondary='advertisement_campaign_association',back_populates='campaign_advertisements')
    advertisement_influencers=db.relationship('Influencer',secondary='advertisement_influencer_association',back_populates='influencer_advertisements')


    def __repr__(self):
        return f'<Advertisements {self.id}>'





class Campaign(db.Model):
    campaign_id = db.Column(db.Integer, primary_key=True,autoincrement=True)
    sponsor_id = db.Column(db.Integer, db.ForeignKey('sponsor.sponsor_id'),nullable=False)
    campaign_name = db.Column(db.String(80))
    revenue_expected = db.Column(db.Integer)
    revenue_received = db.Column(db.Integer, nullable=True)
    success_rate = db.Column(db.Integer, nullable=True)
    start_date = db.Column(db.Date, nullable=True)
    end_date = db.Column(db.Date, nullable=True)
    campaign_niche = db.Column(db.String(80), db.ForeignKey('niche.niche_name'))
    advertisement_id=db.Column(db.Integer,db.ForeignKey('advertisement.id'))
    visibility=db.Column(db.String(1),nullable=True)
    
    
    campaign_funds = db.relationship('Fund', secondary='campaign_fund_association', back_populates='fund_campaigns')
    campaign_niches = db.relationship('Niche', secondary='campaign_niche_association', back_populates='niche_campaigns')
    campaign_sponsors = db.relationship('Sponsor', secondary='campaign_sponsor_association', back_populates='sponsor_campaigns')
    campaign_advertisements = db.relationship('Advertisement', secondary='advertisement_campaign_association', back_populates='advertisement_campaigns')
    def __repr__(self):
        return f'<Campaign {self.campaign_name}>'






class Fund(db.Model):
    fund_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    influencer_id = db.Column(db.Integer, db.ForeignKey('influencer.influencer_id'))
    sponsor_id=db.Column(db.Integer,db.ForeignKey('sponsor.sponsor_id'))
    campaign_id = db.Column(db.Integer, db.ForeignKey('campaign.campaign_id'))
    amount = db.Column(db.Integer)
    
    fund_influencers = db.relationship('Influencer', secondary='fund_influencer_association', back_populates='influencer_funds')
    fund_sponsors = db.relationship('Sponsor', secondary='fund_sponsor_association', back_populates='sponsor_funds')
    fund_campaigns = db.relationship('Campaign', secondary='campaign_fund_association', back_populates='campaign_funds')


    def __repr__(self):
        return f'<fund {self.campaign_id}>'
    







class Influencer(db.Model):
    influencer_id= db.Column(db.Integer,primary_key=True,autoincrement=True)
    influencer_advertisement=db.Column(db.Integer,db.ForeignKey('advertisement.id'))
    influencer_fund=db.Column(db.Integer,db.ForeignKey('fund.fund_id'))
    influencer_user = db.Column(db.Integer,db.ForeignKey('user.user_id'))
    influencer_reach = db.Column(db.Integer)
    influencer_rating = db.Column(db.Float)
    
    influencer_advertisements=db.relationship('Advertisement',secondary='advertisement_influencer_association',back_populates='advertisement_influencers')
    influencer_funds=db.relationship('Fund',secondary='fund_influencer_association',back_populates='fund_influencers')
    influencer_users=db.relationship('User',secondary='influencer_user_association',back_populates='user_influencers')

    def __repr__(self):
        return f'<Influencer {self.influencer_id}>'





class Niche(db.Model):
    niche_id = db.Column(db.Integer, primary_key=True,autoincrement=True)
    parent_niche = db.Column(db.String(80),nullable=True)
    niche_name = db.Column(db.String(80))
    niche_population = db.Column(db.Integer)
    niche_campaigns = db.relationship('Campaign', secondary='campaign_niche_association', back_populates='campaign_niches')
    niche_advertisements = db.relationship('Advertisement', secondary='advertisement_niche_association', back_populates='advertisement_niches')

    def __repr__(self):
        return f'<Niche {self.niche_name}>'





class Role(db.Model):
    __tablename__ = 'Role'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(80), unique=True, nullable=False)
    description = db.Column(db.String(255), nullable=True)

    role_users = db.relationship('User', secondary='role_user_association', back_populates='user_roles')


    def __repr__(self):
        return f'<Role {self.id}>'






class Sponsor(db.Model):
    sponsor_id=db.Column(db.Integer,primary_key=True,autoincrement=True)
    sponsor_fund=db.Column(db.Integer,db.ForeignKey('fund.fund_id'))
    sponsor_company=db.Column(db.String(80),nullable=False)
    sponsor_campaign=db.Column(db.Integer,db.ForeignKey('campaign.campaign_id'))
    
    sponsor_users=db.relationship('User',secondary='sponsor_user_association',back_populates='user_sponsors')
    sponsor_funds=db.relationship('Fund',secondary='fund_sponsor_association',back_populates='fund_sponsors')
    sponsor_campaigns=db.relationship('Campaign',secondary='campaign_sponsor_association',back_populates='campaign_sponsors')
    
    
    def __repr__(self):
        return f'<Sponsor {self.sponsor_company}>'





    
class User(db.Model):
    user_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_password = db.Column(db.String(80), nullable=False)
    user_role = db.Column(db.String(80), nullable=False)
    user_mail = db.Column(db.String(80), unique=True, nullable=False)
    user_name = db.Column(db.String(80), nullable=False)
    influencer_id=db.Column(db.Integer,db.ForeignKey('influencer.influencer_id'),nullable=True)
    sponsor_id=db.Column(db.Integer,db.ForeignKey('sponsor.sponsor_id'),nullable=True)

    user_roles = db.relationship('Role', secondary='role_user_association', back_populates='role_users')
    user_influencers=db.relationship('Influencer',secondary='influencer_user_association',back_populates='influencer_users')
    user_sponsors=db.relationship('Sponsor',secondary='sponsor_user_association',back_populates='sponsor_users')
    
    def if_sponsor(self,company):
        if(self.user_role=='Sponsor'):
            sponsor_entry = Sponsor(
                sponsor_company=company
            )
            db.session.add(sponsor_entry)
            self.sponsor_id=sponsor_entry.sponsor_id
    
                
    def if_influencer(self,reach):  
        if(self.user_role=='Influencer'):
            influencer_entry = Influencer(
                user_id=self.user_id,
                user_password=self.user_password,
                user_role=self.user_role,
                user_mail=self.user_mail,
                user_name=self.user_name,
                influencer_reach=reach
            )
            db.session.add(influencer_entry)

    def __repr__(self):
        return f'<User {self.user_id}>'



#----------------------------------------------RELATION TABLES----------------------------------------------
#----------------------------------------------RELATION TABLES----------------------------------------------
#----------------------------------------------RELATION TABLES----------------------------------------------
#----------------------------------------------RELATION TABLES----------------------------------------------
#----------------------------------------------RELATION TABLES----------------------------------------------
#----------------------------------------------RELATION TABLES----------------------------------------------
#----------------------------------------------RELATION TABLES----------------------------------------------
#----------------------------------------------RELATION TABLES----------------------------------------------
#----------------------------------------------RELATION TABLES----------------------------------------------
#----------------------------------------------RELATION TABLES----------------------------------------------
#----------------------------------------------RELATION TABLES----------------------------------------------
#----------------------------------------------RELATION TABLES----------------------------------------------
#----------------------------------------------RELATION TABLES----------------------------------------------
#----------------------------------------------RELATION TABLES----------------------------------------------
#----------------------------------------------RELATION TABLES----------------------------------------------





class AdvertisementCampaign(db.Model):
    __tablename__='advertisement_campaign_association'
    advertisement_campaign_id = db.Column(db.Integer, primary_key=True)
    campaign_id = db.Column(db.Integer, db.ForeignKey('campaign.campaign_id'))
    advertisement_id = db.Column(db.Integer, db.ForeignKey('advertisement.id'))
    
    def __repr__(self):
        return f'<AdvertisementCampaign {self.Advertisement_campaign_id}>'
        
    
    
    
    

class AdvertisementInfluencer(db.Model):
    __tablename__='advertisement_influencer_association'
    advertisement_influencer_id = db.Column(db.Integer, primary_key=True)
    
    advertisement_id = db.Column(db.Integer, db.ForeignKey('advertisement.id'))
    influencer_id = db.Column(db.Integer, db.ForeignKey('influencer.influencer_id'))  
      
    def __repr__(self):
        return f'<AdvertisementInfluencer {self.Advertisement_influencer_id}>'






class AdvertisementNiche(db.Model):
    __tablename__='advertisement_niche_association'
    advertisement_niche_id = db.Column(db.Integer, primary_key=True)
    niche_id = db.Column(db.Integer, db.ForeignKey('niche.niche_id'))
    advertisement_id = db.Column(db.Integer, db.ForeignKey('advertisement.id'))
    
    def __repr__(self):
        return f'<AdvertisementNicge {self.Advertisement_niche_id}>'





class CampaignNiche(db.Model):
    __tablename__='campaign_niche_association'
    campaign_niche_id = db.Column(db.Integer, primary_key=True)
    niche_id = db.Column(db.Integer, db.ForeignKey('niche.niche_id'))
    campaign_id = db.Column(db.Integer, db.ForeignKey('campaign.campaign_id'))
    
    def __repr__(self):
        return f'<CampaignNiche {self.campaign_niche_id}>'
    
    
    
    

class CampaignSponsor(db.Model):
    __tablename__='campaign_sponsor_association'
    
    campaign_sponsor_id = db.Column(db.Integer,primary_key=True)
    campaign_id=db.Column(db.Integer,db.ForeignKey('campaign.campaign_id'))
    sponsor_id=db.Column(db.Integer,db.ForeignKey('sponsor.sponsor_id'))
    
    def __repr__(self):
        return f'<CampaignSponsor {self.campaign_sponsor_id}>'





class CampaignFund(db.Model):
    __tablename__='campaign_fund_association'
    
    campaign_user_id = db.Column(db.Integer,primary_key=True)
    campaign_id=db.Column(db.Integer,db.ForeignKey('campaign.campaign_id'))
    fund_id=db.Column(db.Integer,db.ForeignKey('fund.fund_id'))
    
    def __repr__(self):
        return f'<CampaignFund {self.campaign_fund_id}>'

    
    
    
    

class FundInfluencer(db.Model):
    __tablename__='fund_influencer_association'
    fund_influencer_id = db.Column(db.Integer, primary_key=True)
    fund_id = db.Column(db.Integer, db.ForeignKey('fund.fund_id'))
    influencer_id = db.Column(db.Integer, db.ForeignKey('influencer.influencer_id'))
    
    def __repr__(self):
        return f'<FundInfluencer {self.fund_influencer_id}>'
    
    
    
    
    

class FundSponsor(db.Model):
    __tablename__='fund_sponsor_association'
    fund_sponsor_id = db.Column(db.Integer, primary_key=True)
    fund_id = db.Column(db.Integer, db.ForeignKey('fund.fund_id'))
    sponsor_id = db.Column(db.Integer, db.ForeignKey('sponsor.sponsor_id'))
    
    def __repr__(self):
        return f'<FundInfluencer {self.fund_influencer_id}>'

    
 
 
 
    
class InfluencerUser(db.Model):
    __tablename__='influencer_user_association'
    
    influencer_user_id = db.Column(db.Integer,primary_key=True)
    influencer_id=db.Column(db.Integer,db.ForeignKey('influencer.influencer_id'))
    user_id=db.Column(db.Integer,db.ForeignKey('user.user_id'))
    
    def __repr__(self):
        return f'<InfluencerUser {self.influencer_user_id}>'





    
class RoleUser(db.Model):
    __tablename__ = 'role_user_association'
    userrole_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.user_id'), nullable=False)
    role_id = db.Column(db.Integer, db.ForeignKey('Role.id'), nullable=False)

    def __repr__(self):
        return f'<RoleUser {self.userrole_id}>'






class SponsorUser(db.Model):
    __tablename__='sponsor_user_association'
    
    sponsor_user_id = db.Column(db.Integer,primary_key=True)
    sponsor_id=db.Column(db.Integer,db.ForeignKey('sponsor.sponsor_id'))
    user_id=db.Column(db.Integer,db.ForeignKey('user.user_id'))
    
    def __repr__(self):
        return f'<SponsorUser {self.sponsor_user_id}>'