'''
Created on 1.11.2016

@author: Timo Nallikari
'''

import time

from gramps.gen.const import GRAMPS_LOCALE as glocale
from gramps.gen.lib import RepoRef
from gramps.gen.lib import Repository
from gramps.gen.lib import RepositoryType
from gramps.gen.lib import Source
from gramps.gen.lib import Tag
from gramps.gen.utils import id


try:
    _trans = glocale.get_addon_translator(__file__)
except ValueError:
    _trans = glocale.translation
_ = _trans.gettext

class CreateGrampsObject:
 
    chgtime = 0
           
    def __init__(self):
        print("CreateGrampsObject init")
        self.chgtime = int(time.time())
        print("   chgtime = " + str(self.chgtime))         

    def buildTag(self, tname, thandle = None):
        if thandle == None:
            thandle = id.create_id()   # 26-merkkinen tunniste
        tag = Tag()
        tag.set_name(tname)
        tag.set_change_time(self.chgtime)
#        tag.set_color("#EF2929")
        tag.set_handle(thandle)   
#        print ("Tag ") ; print(tag.to_struct())
        return ([tag, thandle])
    
    def buildRepository(self, ridno, rname, tag, rtype, rhandle = None):
        if rhandle == None:
            rhandle = id.create_id()   # 26-merkkinen tunniste
        repositoryType = RepositoryType()
        repositoryType.set(rtype)       
    
        repository = Repository()
        repository.set_type(repositoryType)
        repository.set_handle(rhandle)
        repository.set_gramps_id(ridno)
        repository.set_name(rname)
        repository.set_change_time(self.chgtime)
#       repository.set_color("#000000")
        repository.add_tag(tag.get_handle())
#        print ("Repository ") ; print(repository.to_struct())
        return ([repository, rhandle])
    
    def buildSource(self, sidno, stitle, tag, repository, shandle, attribs):
        if shandle == None:
            shandle = id.create_id()   # 26-merkkinen tunniste
#        repositoryType = RepositoryType()
        source = Source()
        source.set_handle(shandle)
        source.set_gramps_id(sidno)
        source.set_title(stitle)
        source.set_author(attribs[0])
        source.set_publication_info(attribs[1])
        source.set_abbreviation(attribs[2])
        source.add_tag(tag.get_handle())
        repoRef = RepoRef()
        repoRef.set_reference_handle(repository.get_handle()) 
        source.add_repo_reference(repoRef)
        source.set_change_time(self.chgtime)
#        source.set_color("#000000")
#        print ("Source ") ; print(source.to_struct())
        return ([source, shandle])

