from pywikibot import family                                                    

class Family(family.Family):                                                    
    def __init__(self):                                                         
        family.Family.__init__(self)                                            
        self.name = 'vdj'                                                       
        self.langs = {                                                          
            'fr': 'leviolondejos.wiki',                                
        }


    def scriptpath(self, code):
        return ''

    def isPublic(self):
        return False