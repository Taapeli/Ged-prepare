'''
Created on 1.11.2016

@author: Timo Nallikarihttp://download.eclipse.org/egit/updates
'''

import time
from gramps.gen.lib import RepositoryType, Repository, RepoRef, Source, Tag
from gramps.gen.utils import id
from gramps.gen.const import GRAMPS_LOCALE as glocale
_ = glocale.translation.gettext

class CreateGrampsObject:
 
    chgtime = 0
           
    def __init__(self):
        print("CreateGrampsObject init")
        self.chgtime = int(time.time())
        print("   chgtime = " + str(self.chgtime))         

    def buildTag(self, tname): 
        tag = Tag()
        tag.set_name(tname)
        tag.set_change_time(self.chgtime)
#        tag.set_color("#EF2929")
        tag.set_handle(id.create_id())   # 26-merkkinen tunniste
#        print ("Tag ") ; print(tag.to_struct())
        return (tag)
    
    def buildRepository(self, ridno, rname, tag, rtype):
        repositoryType = RepositoryType()
        repositoryType.set(rtype)       
    
        repository = Repository()
        repository.set_type(repositoryType)
        repository.set_handle(id.create_id())
        repository.set_gramps_id(ridno)
        repository.set_name(rname)
        repository.set_change_time(self.chgtime)
#       repository.set_color("#000000")
        repository.add_tag(tag.get_handle())
#        print ("Repository ") ; print(repository.to_struct())
        return (repository)
    
    def buildSource(self, sidno, stitle, tag, repository):
        source = Source()
        source.set_handle(id.create_id())
        source.set_gramps_id(sidno)
        source.set_title(stitle)
        source.add_tag(tag.get_handle())
        repoRef = RepoRef()
        repoRef.set_reference_handle(repository.get_handle()) 
        source.add_repo_reference(repoRef)
        source.set_change_time(self.chgtime)
#        source.set_color("#000000")
#        print ("Source ") ; print(source.to_struct())
        return (source)

