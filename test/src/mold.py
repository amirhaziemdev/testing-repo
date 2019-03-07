'''
do we know what we need for Mold class yet?
We do know that we need ID (0-7) and status (Boolean e.g. True or False)
Do we need centres? This might overcomplicate things
'''
class Mold():
    def __init__(self, ID, status, centreX, centreY):
        self.ID = ID
        self.status = status
        self.centreX = centreX
        self.centreY = centreY
    
    def get_ID(self):
        return self.ID
    
    def get_status(self):
        return self.status
    
    #call for destroy
    def destroy(self):
        self.ID.delete()
        self.status.delete()