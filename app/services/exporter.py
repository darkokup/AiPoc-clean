"""Export functionality for various clinical trial data formats."""
from typing import Dict, Any
import json
from datetime import datetime
from xml.etree.ElementTree import Element, SubElement, tostring
from xml.dom import minidom
from app.models.schemas import (
    ProtocolStructured,
    CRFSchema,
    ExportFormat,
)


class ProtocolExporter:
    """Exports protocols and CRFs to various formats."""
    
    def export(
        self,
        protocol: ProtocolStructured,
        crf_schema: CRFSchema,
        format: ExportFormat,
        include_protocol: bool = True,
        include_crf: bool = True,
    ) -> Dict[str, Any]:
        """Export to specified format."""
        
        if format == ExportFormat.ODM_XML:
            return self._export_odm_xml(protocol, crf_schema, include_protocol, include_crf)
        elif format == ExportFormat.FHIR_JSON:
            return self._export_fhir_json(protocol, crf_schema, include_protocol, include_crf)
        elif format == ExportFormat.CSV:
            return self._export_csv(crf_schema)
        elif format == ExportFormat.JSON:
            return self._export_json(protocol, crf_schema, include_protocol, include_crf)
        else:
            raise ValueError(f"Unsupported export format: {format}")
    
    def _export_odm_xml(
        self,
        protocol: ProtocolStructured,
        crf_schema: CRFSchema,
        include_protocol: bool,
        include_crf: bool,
    ) -> Dict[str, str]:
        """Export to CDISC ODM XML format."""
        
        # Create root ODM element
        odm = Element("ODM")
        odm.set("xmlns", "http://www.cdisc.org/ns/odm/v1.3")
        odm.set("xmlns:xsi", "http://www.w3.org/2001/XMLSchema-instance")
        odm.set("ODMVersion", "1.3.2")
        odm.set("FileOID", f"ODM.{protocol.protocol_id}.{datetime.now().strftime('%Y%m%d%H%M%S')}")
        odm.set("FileType", "Snapshot")
        odm.set("CreationDateTime", datetime.now().isoformat())
        odm.set("AsOfDateTime", datetime.now().isoformat())
        odm.set("SourceSystem", "Clinical Trial Protocol Generator")
        odm.set("SourceSystemVersion", "1.0")
        
        # Study
        study = SubElement(odm, "Study")
        study.set("OID", protocol.protocol_id)
        
        # Global Variables
        global_vars = SubElement(study, "GlobalVariables")
        
        study_name = SubElement(global_vars, "StudyName")
        study_name.text = protocol.title
        
        study_desc = SubElement(global_vars, "StudyDescription")
        study_desc.text = f"{protocol.phase} {protocol.study_design} study in {protocol.indication}"
        
        protocol_name = SubElement(global_vars, "ProtocolName")
        protocol_name.text = protocol.protocol_id
        
        # MetaDataVersion
        metadata = SubElement(study, "MetaDataVersion")
        metadata.set("OID", f"MDV.{protocol.protocol_id}.{protocol.version}")
        metadata.set("Name", f"Study MetaData Version {protocol.version}")
        metadata.set("Description", f"Metadata for {protocol.title}")
        
        if include_protocol:
            # Protocol section
            protocol_elem = SubElement(metadata, "Protocol")
            
            # Description
            desc = SubElement(protocol_elem, "Description")
            translated = SubElement(desc, "TranslatedText")
            translated.set("xml:lang", "en")
            translated.text = f"{protocol.phase} {protocol.study_design} study evaluating treatment in patients with {protocol.indication}"
            
            # Objectives
            for obj_type, obj_text in protocol.objectives.items():
                study_obj = SubElement(protocol_elem, "StudyObjective")
                study_obj.set("OID", f"OBJ.{obj_type.upper()}")
                
                obj_desc = SubElement(study_obj, "Description")
                obj_trans = SubElement(obj_desc, "TranslatedText")
                obj_trans.set("xml:lang", "en")
                obj_trans.text = obj_text
            
            # Study Event References (Visit Schedule)
            for i, visit in enumerate(crf_schema.visits, 1):
                event_ref = SubElement(protocol_elem, "StudyEventRef")
                event_ref.set("StudyEventOID", f"SE.{visit.visit_id}")
                event_ref.set("OrderNumber", str(i))
                event_ref.set("Mandatory", "Yes")
            
            # Treatment Arms
            for i, arm in enumerate(protocol.treatment_arms, 1):
                arm_elem = SubElement(protocol_elem, "Arm")
                arm_elem.set("OID", f"ARM.{i}")
                arm_elem.set("Name", arm)
                
                arm_desc = SubElement(arm_elem, "Description")
                arm_trans = SubElement(arm_desc, "TranslatedText")
                arm_trans.set("xml:lang", "en")
                arm_trans.text = arm
            
            # Inclusion/Exclusion Criteria
            if protocol.inclusion_criteria or protocol.exclusion_criteria:
                criteria = SubElement(protocol_elem, "InclusionExclusionCriteria")
                
                # Inclusion Criteria
                if protocol.inclusion_criteria:
                    for i, criterion in enumerate(protocol.inclusion_criteria, 1):
                        inc = SubElement(criteria, "Criterion")
                        inc.set("OID", f"IC.{i}")
                        inc.set("Type", "Inclusion")
                        
                        crit_desc = SubElement(inc, "Description")
                        crit_trans = SubElement(crit_desc, "TranslatedText")
                        crit_trans.set("xml:lang", "en")
                        crit_trans.text = criterion
                
                # Exclusion Criteria
                if protocol.exclusion_criteria:
                    for i, criterion in enumerate(protocol.exclusion_criteria, 1):
                        exc = SubElement(criteria, "Criterion")
                        exc.set("OID", f"EC.{i}")
                        exc.set("Type", "Exclusion")
                        
                        crit_desc = SubElement(exc, "Description")
                        crit_trans = SubElement(crit_desc, "TranslatedText")
                        crit_trans.set("xml:lang", "en")
                        crit_trans.text = criterion
            
            # Study Endpoints
            if protocol.endpoints:
                for i, endpoint in enumerate(protocol.endpoints, 1):
                    endpoint_elem = SubElement(protocol_elem, "StudyEndPoint")
                    endpoint_elem.set("OID", f"EP.{i}")
                    endpoint_elem.set("Type", endpoint.get("type", "primary").capitalize())
                    
                    ep_desc = SubElement(endpoint_elem, "Description")
                    ep_trans = SubElement(ep_desc, "TranslatedText")
                    ep_trans.set("xml:lang", "en")
                    ep_desc_text = endpoint.get("name", endpoint.get("description", ""))
                    if endpoint.get("measurement_timepoint"):
                        ep_desc_text += f" at {endpoint.get('measurement_timepoint')}"
                    ep_trans.text = ep_desc_text
            
            # Conditions (Indication)
            condition = SubElement(protocol_elem, "Condition")
            condition.set("OID", "COND.01")
            cond_desc = SubElement(condition, "Description")
            cond_trans = SubElement(cond_desc, "TranslatedText")
            cond_trans.set("xml:lang", "en")
            cond_trans.text = protocol.indication
            
            # Study Event References (Visit Schedule)
            for visit in crf_schema.visits:
                event_def = SubElement(metadata, "StudyEventDef")
                event_def.set("OID", f"SE.{visit.visit_id}")
                event_def.set("Name", visit.visit_name)
                event_def.set("Repeating", "No")
                event_def.set("Type", "Scheduled")
                
                # Visit description
                visit_desc = SubElement(event_def, "Description")
                visit_trans = SubElement(visit_desc, "TranslatedText")
                visit_trans.set("xml:lang", "en")
                visit_trans.text = f"{visit.visit_name} - {visit.timepoint}"
                if visit.window:
                    visit_trans.text += f" (Window: {visit.window})"
                
                # Forms for this visit
                for j, form_id in enumerate(visit.forms, 1):
                    form_ref = SubElement(event_def, "FormRef")
                    form_ref.set("FormOID", f"FORM.{form_id}")
                    form_ref.set("OrderNumber", str(j))
                    form_ref.set("Mandatory", "Yes")
        
        if include_crf:
            # Form Definitions
            for form in crf_schema.forms:
                form_def = SubElement(metadata, "FormDef")
                form_def.set("OID", f"FORM.{form.form_id}")
                form_def.set("Name", form.form_name)
                form_def.set("Repeating", "Yes" if form.repeating else "No")
                
                # Form description
                if form.form_description:
                    form_desc = SubElement(form_def, "Description")
                    form_trans = SubElement(form_desc, "TranslatedText")
                    form_trans.set("xml:lang", "en")
                    form_trans.text = form.form_description
                
                # Item Group (one per form for simplicity)
                item_group_ref = SubElement(form_def, "ItemGroupRef")
                item_group_ref.set("ItemGroupOID", f"IG.{form.form_id}")
                item_group_ref.set("Mandatory", "Yes")
                item_group_ref.set("OrderNumber", "1")
            
            # Item Group Definitions
            for form in crf_schema.forms:
                item_group = SubElement(metadata, "ItemGroupDef")
                item_group.set("OID", f"IG.{form.form_id}")
                item_group.set("Name", f"{form.form_name} Items")
                item_group.set("Repeating", "No")
                
                # Item Group description
                ig_desc = SubElement(item_group, "Description")
                ig_trans = SubElement(ig_desc, "TranslatedText")
                ig_trans.set("xml:lang", "en")
                ig_trans.text = f"Item group for {form.form_name}"
                
                # Items (fields)
                for j, field in enumerate(form.fields, 1):
                    item_ref = SubElement(item_group, "ItemRef")
                    item_ref.set("ItemOID", f"IT.{field.field_id}")
                    item_ref.set("OrderNumber", str(j))
                    item_ref.set("Mandatory", "Yes" if field.required else "No")
                    
                    # SDTM mapping if available
                    if field.sdtm_variable:
                        role_elem = SubElement(item_ref, "Role")
                        role_elem.set("RoleCodeListOID", "CL.ROLE")
                        role_elem.text = field.sdtm_variable
            
            # Item Definitions
            for form in crf_schema.forms:
                for field in form.fields:
                    item_def = SubElement(metadata, "ItemDef")
                    item_def.set("OID", f"IT.{field.field_id}")
                    item_def.set("Name", field.field_name)
                    item_def.set("DataType", self._map_datatype_to_odm(field.data_type))
                    
                    # Question
                    question = SubElement(item_def, "Question")
                    translated_text = SubElement(question, "TranslatedText")
                    translated_text.set("xml:lang", "en")
                    translated_text.text = field.field_label
                    
                    # Description with field details
                    item_desc = SubElement(item_def, "Description")
                    item_trans = SubElement(item_desc, "TranslatedText")
                    item_trans.set("xml:lang", "en")
                    desc_text = f"{field.field_label}"
                    if field.required:
                        desc_text += " (Required)"
                    if field.validation_rules:
                        desc_text += f" - Validation: {json.dumps(field.validation_rules)}"
                    item_trans.text = desc_text
                    
                    # CDASH mapping if available
                    if field.cdash_variable:
                        alias = SubElement(item_def, "Alias")
                        alias.set("Context", "CDASH")
                        alias.set("Name", field.cdash_variable)
                    
                    # SDTM mapping if available
                    if field.sdtm_variable:
                        alias = SubElement(item_def, "Alias")
                        alias.set("Context", "SDTM")
                        alias.set("Name", field.sdtm_variable)
                    
                    # Controlled terminology reference
                    if field.controlled_vocabulary:
                        ct_ref = SubElement(item_def, "CodeListRef")
                        ct_ref.set("CodeListOID", f"CL.{field.controlled_vocabulary}")
            
            # Add CodeLists for common controlled terminologies
            self._add_common_codelists(metadata)
            
            # Add study parameters
            self._add_study_parameters(metadata, protocol)
            
            # Add method definitions (for calculations, edit checks)
            self._add_method_definitions(metadata, protocol, crf_schema)
            
            # Add measurement units
            self._add_measurement_units(metadata)
        
        # Clinical Data section (template for data collection)
        self._add_clinical_data_template(odm, protocol)
        
        # Convert to pretty XML string
        xml_str = minidom.parseString(tostring(odm)).toprettyxml(indent="  ")
        
        return {
            "format": "odm_xml",
            "content": xml_str,
            "filename": f"{protocol.protocol_id}_ODM.xml",
        }
    
    def _add_common_codelists(self, metadata: Element):
        """Add common CDISC codelists to ODM."""
        
        # Yes/No codelist
        yn_list = SubElement(metadata, "CodeList")
        yn_list.set("OID", "CL.NY")
        yn_list.set("Name", "No Yes Response")
        yn_list.set("DataType", "text")
        
        yn_no = SubElement(yn_list, "CodeListItem")
        yn_no.set("CodedValue", "N")
        decode = SubElement(yn_no, "Decode")
        trans = SubElement(decode, "TranslatedText")
        trans.set("xml:lang", "en")
        trans.text = "No"
        
        yn_yes = SubElement(yn_list, "CodeListItem")
        yn_yes.set("CodedValue", "Y")
        decode = SubElement(yn_yes, "Decode")
        trans = SubElement(decode, "TranslatedText")
        trans.set("xml:lang", "en")
        trans.text = "Yes"
        
        # Sex codelist
        sex_list = SubElement(metadata, "CodeList")
        sex_list.set("OID", "CL.SEX")
        sex_list.set("Name", "Sex")
        sex_list.set("DataType", "text")
        
        for code, text in [("M", "Male"), ("F", "Female"), ("U", "Unknown")]:
            item = SubElement(sex_list, "CodeListItem")
            item.set("CodedValue", code)
            decode = SubElement(item, "Decode")
            trans = SubElement(decode, "TranslatedText")
            trans.set("xml:lang", "en")
            trans.text = text
    
    def _add_study_parameters(self, metadata: Element, protocol: ProtocolStructured):
        """Add study parameters to ODM."""
        
        # Study parameters
        params = SubElement(metadata, "StudyParameterListRef")
        params.set("StudyParameterListOID", "SPL.COMMON")
        
        param_list = SubElement(metadata, "StudyParameterList")
        param_list.set("OID", "SPL.COMMON")
        
        # Sample size
        param = SubElement(param_list, "StudyParameter")
        param.set("OID", "SP.SAMPLE_SIZE")
        param.set("Name", "Sample Size")
        param.text = str(protocol.sample_size)
        
        # Study duration
        param = SubElement(param_list, "StudyParameter")
        param.set("OID", "SP.DURATION")
        param.set("Name", "Study Duration (weeks)")
        param.text = str(protocol.duration_weeks)
        
        # Phase
        param = SubElement(param_list, "StudyParameter")
        param.set("OID", "SP.PHASE")
        param.set("Name", "Study Phase")
        param.text = protocol.phase
    
    def _add_method_definitions(self, metadata: Element, protocol: ProtocolStructured, crf_schema: CRFSchema):
        """Add method definitions for calculations and edit checks."""
        
        # Statistical Analysis Method
        if protocol.statistical_plan:
            method = SubElement(metadata, "MethodDef")
            method.set("OID", "MT.STATISTICAL")
            method.set("Name", "Statistical Analysis Plan")
            method.set("Type", "Computation")
            
            method_desc = SubElement(method, "Description")
            method_trans = SubElement(method_desc, "TranslatedText")
            method_trans.set("xml:lang", "en")
            
            # Build statistical plan description
            stat_desc = "Statistical Analysis Plan: "
            if isinstance(protocol.statistical_plan, dict):
                stat_parts = []
                for key, value in protocol.statistical_plan.items():
                    if isinstance(value, (str, int, float)):
                        stat_parts.append(f"{key}: {value}")
                stat_desc += "; ".join(stat_parts)
            else:
                stat_desc += str(protocol.statistical_plan)
            
            method_trans.text = stat_desc
        
        # Edit checks for field validations
        validation_id = 1
        for form in crf_schema.forms:
            for field in form.fields:
                if field.validation_rules:
                    method = SubElement(metadata, "MethodDef")
                    method.set("OID", f"MT.VALIDATION.{validation_id}")
                    method.set("Name", f"Validation for {field.field_name}")
                    method.set("Type", "Computation")
                    
                    method_desc = SubElement(method, "Description")
                    method_trans = SubElement(method_desc, "TranslatedText")
                    method_trans.set("xml:lang", "en")
                    
                    val_desc = f"Validation rules for {field.field_label}: "
                    rules = []
                    for rule_key, rule_value in field.validation_rules.items():
                        rules.append(f"{rule_key}={rule_value}")
                    val_desc += ", ".join(rules)
                    
                    method_trans.text = val_desc
                    
                    # Add formal expression if applicable
                    if "min" in field.validation_rules or "max" in field.validation_rules:
                        formal_expr = SubElement(method, "FormalExpression")
                        formal_expr.set("Context", "Python")
                        
                        expr_parts = []
                        if "min" in field.validation_rules:
                            expr_parts.append(f"value >= {field.validation_rules['min']}")
                        if "max" in field.validation_rules:
                            expr_parts.append(f"value <= {field.validation_rules['max']}")
                        
                        formal_expr.text = " and ".join(expr_parts)
                    
                    validation_id += 1
    
    def _add_measurement_units(self, metadata: Element):
        """Add common measurement units."""
        
        # Common units
        units = [
            ("UNIT.KG", "Kilograms", "kg"),
            ("UNIT.CM", "Centimeters", "cm"),
            ("UNIT.MMHG", "Millimeters of Mercury", "mmHg"),
            ("UNIT.BEATS_MIN", "Beats per Minute", "beats/min"),
            ("UNIT.CELSIUS", "Degrees Celsius", "°C"),
            ("UNIT.PERCENT", "Percentage", "%"),
            ("UNIT.MG_DL", "Milligrams per Deciliter", "mg/dL"),
            ("UNIT.MMOL_L", "Millimoles per Liter", "mmol/L"),
        ]
        
        for oid, name, symbol in units:
            unit = SubElement(metadata, "MeasurementUnit")
            unit.set("OID", oid)
            unit.set("Name", name)
            
            symbol_elem = SubElement(unit, "Symbol")
            symbol_trans = SubElement(symbol_elem, "TranslatedText")
            symbol_trans.set("xml:lang", "en")
            symbol_trans.text = symbol
    
    def _add_clinical_data_template(self, odm: Element, protocol: ProtocolStructured):
        """Add clinical data template section."""
        
        # ClinicalData section (empty template for data collection)
        clinical_data = SubElement(odm, "ClinicalData")
        clinical_data.set("StudyOID", protocol.protocol_id)
        clinical_data.set("MetaDataVersionOID", f"MDV.{protocol.protocol_id}.{protocol.version}")
        
        # Add comment about this being a template
        comment = SubElement(clinical_data, "Comment")
        comment.text = "This is an empty template. Actual clinical data will be populated during the study."
    
    def _export_fhir_json(
        self,
        protocol: ProtocolStructured,
        crf_schema: CRFSchema,
        include_protocol: bool,
        include_crf: bool,
    ) -> Dict[str, Any]:
        """Export to FHIR JSON format."""
        
        resources = []
        
        if include_protocol:
            # ResearchStudy resource
            research_study = {
                "resourceType": "ResearchStudy",
                "id": protocol.protocol_id,
                "status": "active",
                "title": protocol.title,
                "description": f"{protocol.phase} {protocol.study_design} study in {protocol.indication}",
                "enrollment": [
                    {
                        "reference": f"Group/{protocol.protocol_id}-enrollment"
                    }
                ],
                "period": {
                    "start": datetime.now().isoformat(),
                },
                "sponsor": {
                    "display": protocol.sponsor
                },
                "principalInvestigator": {
                    "display": "To be determined"
                },
                "phase": {
                    "text": protocol.phase
                },
                "category": [
                    {
                        "text": "Interventional"
                    }
                ],
                "focus": [
                    {
                        "text": protocol.indication
                    }
                ],
                "objective": [
                    {
                        "name": "Primary Objective",
                        "type": {
                            "text": "primary"
                        }
                    }
                ],
            }
            resources.append(research_study)
        
        if include_crf:
            # Create Questionnaire resources for each form
            for form in crf_schema.forms:
                questionnaire = {
                    "resourceType": "Questionnaire",
                    "id": f"{protocol.protocol_id}-{form.form_id}",
                    "status": "active",
                    "title": form.form_name,
                    "description": form.form_description,
                    "item": []
                }
                
                for field in form.fields:
                    item = {
                        "linkId": field.field_id,
                        "text": field.field_label,
                        "type": self._map_datatype_to_fhir(field.data_type),
                        "required": field.required,
                    }
                    
                    # Add validation if present
                    if field.validation_rules:
                        if "min" in field.validation_rules:
                            item["extension"] = item.get("extension", [])
                            item["extension"].append({
                                "url": "http://hl7.org/fhir/StructureDefinition/minValue",
                                "valueInteger": field.validation_rules["min"]
                            })
                        if "max" in field.validation_rules:
                            item["extension"] = item.get("extension", [])
                            item["extension"].append({
                                "url": "http://hl7.org/fhir/StructureDefinition/maxValue",
                                "valueInteger": field.validation_rules["max"]
                            })
                    
                    questionnaire["item"].append(item)
                
                resources.append(questionnaire)
        
        bundle = {
            "resourceType": "Bundle",
            "type": "collection",
            "entry": [{"resource": r} for r in resources]
        }
        
        return {
            "format": "fhir_json",
            "content": json.dumps(bundle, indent=2),
            "filename": f"{protocol.protocol_id}_FHIR.json",
        }
    
    def _export_csv(self, crf_schema: CRFSchema) -> Dict[str, Any]:
        """Export CRF schema to CSV format (data dictionary)."""
        
        csv_lines = []
        
        # Header
        csv_lines.append(
            "Form ID,Form Name,Field ID,Field Name,Field Label,Data Type,"
            "Required,CDASH Variable,SDTM Variable,Validation Rules"
        )
        
        # Data rows
        for form in crf_schema.forms:
            for field in form.fields:
                validation = json.dumps(field.validation_rules) if field.validation_rules else ""
                
                csv_lines.append(
                    f'"{form.form_id}","{form.form_name}","{field.field_id}",'
                    f'"{field.field_name}","{field.field_label}","{field.data_type}",'
                    f'"{field.required}","{field.cdash_variable or ""}","'
                    f'{field.sdtm_variable or ""}","{validation}"'
                )
        
        return {
            "format": "csv",
            "content": "\n".join(csv_lines),
            "filename": f"{crf_schema.study_id}_DataDictionary.csv",
        }
    
    def _export_json(
        self,
        protocol: ProtocolStructured,
        crf_schema: CRFSchema,
        include_protocol: bool,
        include_crf: bool,
    ) -> Dict[str, Any]:
        """Export to JSON format."""
        
        export_data = {
            "export_date": datetime.now().isoformat(),
            "study_id": protocol.protocol_id,
        }
        
        if include_protocol:
            export_data["protocol"] = protocol.model_dump()
        
        if include_crf:
            export_data["crf_schema"] = crf_schema.model_dump()
        
        return {
            "format": "json",
            "content": json.dumps(export_data, indent=2, default=str),
            "filename": f"{protocol.protocol_id}_Export.json",
        }
    
    def _map_datatype_to_odm(self, data_type: str) -> str:
        """Map internal data type to ODM data type."""
        mapping = {
            "text": "text",
            "number": "integer",
            "date": "date",
            "datetime": "datetime",
            "dropdown": "text",
            "checkbox": "text",
            "radio": "text",
        }
        return mapping.get(data_type, "text")
    
    def _map_datatype_to_fhir(self, data_type: str) -> str:
        """Map internal data type to FHIR Questionnaire item type."""
        mapping = {
            "text": "string",
            "number": "decimal",
            "date": "date",
            "datetime": "dateTime",
            "dropdown": "choice",
            "checkbox": "choice",
            "radio": "choice",
        }
        return mapping.get(data_type, "string")
