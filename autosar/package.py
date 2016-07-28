import autosar.component
import autosar.behavior
import autosar.element
import copy
import autosar.base

class Package(object):
   packageName = None
   def __init__(self,name,parent=None):
      self.name = name
      self.elements = []
      self.subPackages = []
      self.parent=parent
   @property
   def ref(self):
      if self.parent is not None:
         return self.parent.ref+'/%s'%self.name
      else:
         return None      

   def find(self,ref):
      if ref.startswith('/'): return self.root().find(ref)
      ref = ref.partition('/')      
      name = ref[0]
      for package in self.subPackages:
         if package.name == name:
            if len(ref[2])>0:
               return package.find(ref[2])
            else:
               return package
      for elem in self.elements:
         if elem.name == name:
            if len(ref[2])>0:
               return elem.find(ref[2])
            else:
               return elem
      return None
   
   def findall(self,ref):
      """
      experimental find-method that has some rudimentary support for globs.      
      """
      if ref is None: return None
      if ref[0]=='/': ref=ref[1:] #removes initial '/' if it exists
      ref = ref.partition('/')
      if ref[0]=='*' and len(ref[2])==0:
         result=list(self.elements)
         result.extend(self.subPackages)
      else:
         result=[]
         for item in (self.packages+self.subPackages):
            if item.name == ref[0] or ref[0]=='*':
               if len(ref[2])>0:
                  result.extend(item.findall(ref[2]))
               else:
                  result.append(item)
      return result      
   
   def dir(self,ref=None,_prefix=''):
      if ref==None:
         return [_prefix+x.name for x in self.subPackages]+[_prefix+x.name for x in self.elements]      
      else:
         ref = ref.partition('/')
         result=self.find(ref[0])
         if result is not None:
            return result.dir(ref[2] if len(ref[2])>0 else None,_prefix+ref[0]+'/')
         else:
            return None
      
   
   def asdict(self):
      data={'type':self.__class__.__name__,'name':self.name,'elements':[],'subPackages':[]}
      for element in self.elements:
         if hasattr(element,'asdict'):            
            data['elements'].append(element.asdict())
         else:
            print(type(element))
      for subPackage in self.subPackages:         
         data['subPackages'].append(subPackage.asdict())
      if len(data['elements'])==0: del data['elements']
      if len(data['subPackages'])==0: del data['subPackages']
      return data
   
   def createComponentType(self,name,componentType):
      if componentType is autosar.component.ApplicationSoftwareComponent:         
         swc=autosar.component.ApplicationSoftwareComponent(name,parent=self)
      elif componentType is autosar.component.ComplexDeviceDriverSoftwareComponent:
         swc.autosar.component.ComplexDeviceDriverSoftwareComponent(name,parent=self)
      else:
         raise ValueError(componentType+ "is an unsupported type")
      internalBehavior=autosar.behavior.InternalBehavior('%s_InternalBehavior'%name,self.ref+'/%s'%name,parent=self)
      implementation=autosar.component.SwcImplementation('%s_Implementation'%name,internalBehavior.ref,parent=self)
      swc.behavior=internalBehavior
      swc.implementation=implementation
      self.elements.append(swc)
      self.elements.append(internalBehavior)
      self.elements.append(implementation)
      return swc
   
   # def findWS(self):
   #    """depcrecated, use rootWS() instead"""
   #    return self.rootWS()
         
   def rootWS(self):
      if self.parent is None:
         return None
      else:
         return self.parent.root()
      
   def append(self,elem):
      """appends elem to the self.elements list"""
      if isinstance(elem,autosar.element.Element):         
         self.elements.append(elem)
         elem.parent=self
      elif isinstance(elem,Package):
        self.subPackages.append(elem)
        elem.parent=self
      else:
         raise ValueError('unexpected value type %s'%str(type(elem)))

   def update(self,other):
      """copies/clones each element from other into self.elements"""
      if type(self) == type(other):
         for otherElem in other.elements:            
            newElem=copy.deepcopy(otherElem)
            assert(newElem is not None)
            try:
               i=self.index('elements',otherElem.name)
               oldElem=self.elements[i]
               self.elements[i]=newElem
               oldElem.parent=None               
            except ValueError:
               self.elements.append(newElem)
            newElem.parent=self
      else:
         raise ValueError('cannot update from object of different type')

   def index(self,container,name):
      if container=='elements':
         lst=self.elements
      elif container=='subPackages':
         lst=self.subPackages
      else:
         raise KeyError("%s not in %s"%(container,self.__class__.__name__))
      return autosar.base.indexByName(lst,name)





















