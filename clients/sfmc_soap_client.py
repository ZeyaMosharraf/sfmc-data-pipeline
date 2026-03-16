import xml.etree.ElementTree as ET
from clients.sfmc_client import get_credentials, get_token, get_sfmc_session
from config.sfmc_columns import sfmc_soap_properties
from utils.logger import get_logger

logger = get_logger(__name__)

SOAP_NS = "http://exacttarget.com/wsdl/partnerAPI"


def build_soap_request(continue_request: str = None) -> str:
    token = get_token()
    _, _, subdomain, _ = get_credentials()

    if continue_request:
        body = f"""
        <RetrieveRequestMsg xmlns="{SOAP_NS}">
            <RetrieveRequest>
                <ContinueRequest>{continue_request}</ContinueRequest>
            </RetrieveRequest>
        </RetrieveRequestMsg>"""
    else:
        properties_xml = "\n".join(
            f"<Properties>{prop}</Properties>" for prop in sfmc_soap_properties
        )
        body = f"""
        <RetrieveRequestMsg xmlns="{SOAP_NS}">
            <RetrieveRequest>
                <ObjectType>Send</ObjectType>
                <Options>
                    <BatchSize>2500</BatchSize>
                </Options>
                {properties_xml}
            </RetrieveRequest>
        </RetrieveRequestMsg>"""

    return f"""<?xml version="1.0" encoding="UTF-8"?>
<s:Envelope xmlns:s="http://www.w3.org/2003/05/soap-envelope"
            xmlns:a="http://schemas.xmlsoap.org/ws/2004/08/addressing">
    <s:Header>
        <a:Action s:mustUnderstand="1">Retrieve</a:Action>
        <a:To s:mustUnderstand="1">https://{subdomain}.soap.marketingcloudapis.com/Service.asmx</a:To>
        <fueloauth xmlns="http://exacttarget.com">{token}</fueloauth>
    </s:Header>
    <s:Body xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
            xmlns:xsd="http://www.w3.org/2001/XMLSchema">
        {body}
    </s:Body>
</s:Envelope>"""


def parse_soap_response(xml_text: str) -> tuple[list[dict], str | None, bool]:
    root = ET.fromstring(xml_text)
    ns = {"et": SOAP_NS}

    overall_status = root.findtext(".//et:OverallStatus", namespaces=ns)
    request_id = root.findtext(".//et:RequestID", namespaces=ns)
    has_more = overall_status == "MoreDataAvailable"

    results = []
    body = root.find(".//et:RetrieveResponseMsg", namespaces=ns)
    for result in body.findall("et:Results", namespaces=ns):
        row = {}
        for prop in sfmc_soap_properties:
            tag = prop.replace(".", "_")
            value = result.findtext(f"et:{tag}", namespaces=ns)
            row[prop] = value
        results.append(row)

    logger.info(f"Status: {overall_status} | Records: {len(results)} | RequestID: {request_id}")
    return results, request_id, has_more


def soap_fetch(continue_request: str = None) -> tuple[list[dict], str | None, bool]:
    _, _, subdomain, _ = get_credentials()
    session = get_sfmc_session()

    url = f"https://{subdomain}.soap.marketingcloudapis.com/Service.asmx"
    headers = {
        "Content-Type": "text/xml",
        "SOAPAction": "Retrieve"
    }

    xml_body = build_soap_request(continue_request)

    response = session.post(url, headers=headers, data=xml_body.encode("utf-8"), timeout=60)
    logger.info(f"response status: {response.status_code}")
    response.raise_for_status()

    return parse_soap_response(response.text)