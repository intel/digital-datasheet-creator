# ********************** COPYRIGHT INTEL CORPORATION ***********************
#
# THE SOFTWARE CONTAINED IN THIS FILE IS CONFIDENTIAL AND PROPRIETARY
# TO INTEL CORPORATION. THIS PRINTOUT MAY NOT BE PHOTOCOPIED,
# REPRODUCED, OR USED IN ANY MANNER WITHOUT THE EXPRESSED WRITTEN
# CONSENT OF INTEL CORPORATION. ALL LOCAL, STATE, AND FEDERAL
# LAWS RELATING TO COPYRIGHTED MATERIAL APPLY.
#
# Copyright (c), Intel Corporation
#
# ********************** COPYRIGHT INTEL CORPORATION ***********************

from marshmallow import Schema, fields


class AttachmentEntity(Schema):
    name = fields.Str(required=True)
    reference = fields.Str(required=True)
    type = fields.Str(required=True)


class EDatasheetContentSchema(Schema):
    namespace = fields.String(required=True)
    generatedOn = fields.String(required=True)
    generatedBy = fields.String(required=True)
    inputFile = fields.String(required=True)
    platformAbbreviation = fields.String(required=True)
    sku = fields.String(required=True)
    revision = fields.String(required=True)
    collateral = fields.String(required=True)
    title = fields.String(required=True)
    guid = fields.String(required=True)
    tables = fields.Raw()
    attachments = fields.Nested(AttachmentEntity, many=True)


class EDatasheetEntity(Schema):
    datasheet = fields.Nested(EDatasheetContentSchema, required=True)
