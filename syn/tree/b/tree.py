from syn.base.b import Base, Attr


#-------------------------------------------------------------------------------
# Tree


class Tree(Base):
    _attrs = dict()
    _opts = dict(init_validate = True)

    def validate(self):
        super(Tree, self).validate()
        self.root.validate()


#-------------------------------------------------------------------------------
# __all__

__all__ = ('Tree',)

#-------------------------------------------------------------------------------
