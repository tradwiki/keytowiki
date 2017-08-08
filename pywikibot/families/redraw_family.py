from pywikibot import family                                                    

class Family(family.Family):                                                    
    def __init__(self):                                                         
        family.Family.__init__(self)                                            
        self.name = 'redraw'                                                       
        self.langs = {                                                          
            'fr': 'wiki.procedurable.com',                                
        }


    def scriptpath(self, code):
        return ''

    def isPublic(self):
        return False