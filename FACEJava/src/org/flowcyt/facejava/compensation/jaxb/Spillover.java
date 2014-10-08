//
// This file was generated by the JavaTM Architecture for XML Binding(JAXB) Reference Implementation, v2.0.2-b01-fcs 
// See <a href="http://java.sun.com/xml/jaxb">http://java.sun.com/xml/jaxb</a> 
// Any modifications to this file will be lost upon recompilation of the source schema. 
// Generated on: 2006.08.17 at 04:07:15 PM PDT 
//


package org.flowcyt.facejava.compensation.jaxb;

import java.util.ArrayList;
import java.util.List;
import javax.xml.bind.annotation.XmlAccessType;
import javax.xml.bind.annotation.XmlAccessorType;
import javax.xml.bind.annotation.XmlAttribute;
import javax.xml.bind.annotation.XmlElement;
import javax.xml.bind.annotation.XmlType;


/**
 * 
 * 				A spillover element corresponds to a row of the compensation matrix.
 * 			
 * 
 * <p>Java class for Spillover complex type.
 * 
 * <p>The following schema fragment specifies the expected content contained within this class.
 * 
 * <pre>
 * &lt;complexType name="Spillover">
 *   &lt;complexContent>
 *     &lt;restriction base="{http://www.w3.org/2001/XMLSchema}anyType">
 *       &lt;sequence maxOccurs="unbounded">
 *         &lt;element name="coefficient" type="{http://www.isac-net.org/std/Compensation-ML/v1.0/}Coefficient"/>
 *       &lt;/sequence>
 *       &lt;attribute name="parameter" use="required" type="{http://www.isac-net.org/std/common-types/v1.0/}NonEmptyString" />
 *     &lt;/restriction>
 *   &lt;/complexContent>
 * &lt;/complexType>
 * </pre>
 * 
 * 
 */
@XmlAccessorType(XmlAccessType.FIELD)
@XmlType(name = "Spillover", propOrder = {
    "coefficient"
})
public class Spillover {

    @XmlElement(required = true)
    protected List<Coefficient> coefficient;
    @XmlAttribute(namespace = "http://www.isac-net.org/std/Compensation-ML/v1.0/", required = true)
    protected String parameter;

    /**
     * Gets the value of the coefficient property.
     * 
     * <p>
     * This accessor method returns a reference to the live list,
     * not a snapshot. Therefore any modification you make to the
     * returned list will be present inside the JAXB object.
     * This is why there is not a <CODE>set</CODE> method for the coefficient property.
     * 
     * <p>
     * For example, to add a new item, do as follows:
     * <pre>
     *    getCoefficient().add(newItem);
     * </pre>
     * 
     * 
     * <p>
     * Objects of the following type(s) are allowed in the list
     * {@link Coefficient }
     * 
     * 
     */
    public List<Coefficient> getCoefficient() {
        if (coefficient == null) {
            coefficient = new ArrayList<Coefficient>();
        }
        return this.coefficient;
    }

    /**
     * Gets the value of the parameter property.
     * 
     * @return
     *     possible object is
     *     {@link String }
     *     
     */
    public String getParameter() {
        return parameter;
    }

    /**
     * Sets the value of the parameter property.
     * 
     * @param value
     *     allowed object is
     *     {@link String }
     *     
     */
    public void setParameter(String value) {
        this.parameter = value;
    }

}
