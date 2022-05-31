from sqlalchemy import BigInteger, Boolean, Column, ForeignKey, Identity, Index, Integer, LargeBinary, Unicode, text
from sqlalchemy.dialects.mssql import DATETIME2, DATETIMEOFFSET, UNIQUEIDENTIFIER
from sqlalchemy.orm import declarative_base, relationship

Base = declarative_base()


class ActionToken(Base):
    __tablename__ = 'ActionToken'

    id = Column(BigInteger, Identity(start=1, increment=1), nullable=False, unique=True)
    token = Column(UNIQUEIDENTIFIER, primary_key=True, server_default=text('(newid())'))
    isAddUserToken = Column(Boolean, nullable=False, server_default=text('((0))'))
    isActive = Column(Boolean, nullable=False, server_default=text('((1))'))
    isAddDeviceToken = Column(Boolean, nullable=False, server_default=text('((0))'))

    SubdivisionsUser = relationship('SubdivisionsUser', back_populates='ActionToken')
    Clients = relationship('Clients', back_populates='ActionToken')
    Devices = relationship('Devices', back_populates='ActionToken')


class Sysdiagrams(Base):
    __tablename__ = 'sysdiagrams'
    __table_args__ = (
        Index('UK_principal_name', 'principal_id', 'name', unique=True),
    )

    name = Column(Unicode(128), nullable=False)
    principal_id = Column(Integer, nullable=False)
    diagram_id = Column(Integer, Identity(start=1, increment=1), primary_key=True)
    version = Column(Integer)
    definition = Column(LargeBinary)


class SubdivisionsUser(Base):
    __tablename__ = 'SubdivisionsUser'

    Id = Column(BigInteger, Identity(start=1, increment=1), nullable=False, unique=True)
    idSubdivisionUser = Column(BigInteger, primary_key=True)
    dateCreatedSubdivisionUser = Column(DATETIME2, nullable=False, server_default=text('(getdate())'))
    accessSubdivision = Column(Boolean, nullable=False, server_default=text('((1))'))
    nameSubdivision = Column(Unicode(50), nullable=False)
    identSubdivisionUser = Column(UNIQUEIDENTIFIER, nullable=False, server_default=text('(newid())'))
    actionToken = Column(ForeignKey('ActionToken.token', ondelete='CASCADE', onupdate='CASCADE'), nullable=False)
    email = Column(Unicode(30))
    phone = Column(Unicode(20))
    comment = Column(Unicode)

    ActionToken = relationship('ActionToken', back_populates='SubdivisionsUser')
    Clients = relationship('Clients', back_populates='SubdivisionsUser')
    Devices = relationship('Devices', back_populates='SubdivisionsUser')


class Clients(Base):
    __tablename__ = 'Clients'

    Id = Column(BigInteger, Identity(start=1, increment=1), primary_key=True, unique=True)
    idUser = Column(BigInteger, nullable=False, unique=True)
    idSubdivisionUser = Column(ForeignKey('SubdivisionsUser.idSubdivisionUser'), nullable=False)
    nameUser = Column(Unicode(30), nullable=False, unique=True)
    accessUser = Column(Boolean, nullable=False, server_default=text('((1))'))
    dateCreatedAccount = Column(DATETIME2, nullable=False, server_default=text('(getdate())'))
    identUser = Column(UNIQUEIDENTIFIER, nullable=False, server_default=text('(newid())'))
    email = Column(Unicode(30), nullable=False, unique=True)
    phone = Column(Unicode(20), nullable=False, unique=True)
    password = Column(Unicode(20), nullable=False)
    actionToken = Column(ForeignKey('ActionToken.token', ondelete='CASCADE', onupdate='CASCADE'), nullable=False)

    ActionToken = relationship('ActionToken', back_populates='Clients')
    SubdivisionsUser = relationship('SubdivisionsUser', back_populates='Clients')


class Devices(Base):
    __tablename__ = 'Devices'

    id = Column(BigInteger, Identity(start=1, increment=1), primary_key=True, unique=True)
    idSubdivisionUser = Column(ForeignKey('SubdivisionsUser.idSubdivisionUser'), nullable=False)
    dateCreatedSubdivisionUser = Column(DATETIMEOFFSET, nullable=False, server_default=text('(getdate())'))
    accessSubdivision = Column(Boolean, nullable=False, server_default=text('((1))'))
    demoMode = Column(Boolean, nullable=False, server_default=text('((1))'))
    actionToken = Column(ForeignKey('ActionToken.token', ondelete='CASCADE', onupdate='CASCADE'), nullable=False)
    serialNumberTerminal = Column(Unicode(32), nullable=False, unique=True)
    idDevice = Column(Unicode(50), unique=True)
    nameDevice = Column(Unicode(50))
    nameDataBase = Column(Unicode(50))
    loginDataBase = Column(Unicode(20))
    passwordDataBase = Column(Unicode(20))
    serverDataBase = Column(Unicode(50))
    fileSyncSettings = Column(Unicode)
    confirmCode = Column(Unicode(12), nullable=True)

    ActionToken = relationship('ActionToken', back_populates='Devices')
    SubdivisionsUser = relationship('SubdivisionsUser', back_populates='Devices')
