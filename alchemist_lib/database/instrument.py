from sqlalchemy import Column, Integer, String

from . import Base



class Instrument(Base):

    """
    Map class for table instrument.

        - **instrument_id**: Integer, primary_key.
        - **instrument_type**: String(50), not null.

    Note:
        https://rszalski.github.io/magicmethods/
    """
    
    __tablename__ = "instrument"

    instrument_id = Column(Integer, primary_key = True)
    instrument_type = Column(String(50), nullable = False)
    

    def __init__(self, instrument_type):

        """
        Costructor method.

        Args:
            - instrument_type (str): Type of financial instrument.
        """
        
        self.instrument_type = instrument_type

    
    def __repr__(self):
        return "<Instrument(instrument_type={})>".format(self.instrument_type)


    def to_dict(self):
        
        """
        As the name tell, it returns attributes in a dict form.
        
        Note:
            The __dict__ method is not overrideble.
        """
        
        return {"instrument_id" : self.instrument_id,
                "instrument_type" : self.instrument_type
                }
    

    
    def __eq__(self, other):
        
        """
        Overrides the default implementation.

        Reference:
            https://stackoverflow.com/questions/390250/elegant-ways-to-support-equivalence-equality-in-python-classes
        """

        if isinstance(self, other.__class__):
            return self.to_dict() == other.to_dict()
        return False
    

    def __ne__(self, other):
        
        """
        Overrides the default implementation.
        """
        
        return not self.__eq__(other)
    

    def __lt__(self, other):
        
        """
        Overrides the default implementation.
        """
        
        if isinstance(self, other.__class__):
            return self.instrument_type < other.instrument_type
        return NotImplemented

    def __le__(self, other):

        """
        Overrides the default implementation.
        """
        
        if isinstance(self, other.__class__):
            return self.instrument_type <= other.instrument_type 
        return NotImplemented


    def __gt__(self, other):

        """
        Overrides the default implementation.
        """
        
        if isinstance(self, other.__class__):
            return self.instrument_type > other.instrument_type
        return NotImplemented


    def __ge__(self, other):

        """
        Overrides the default implementation.
        """
        
        if isinstance(self, other.__class__):
            return self.instrument_type >= other.instrument_type
        return NotImplemented


    def __hash__(self):
        
        """
        Overrides the default implementation.
        """
        
        return hash(tuple(sorted(self.to_dict().items())))

    
