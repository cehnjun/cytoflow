//
// This file was generated by the JavaTM Architecture for XML Binding(JAXB) Reference Implementation, v2.0.2-b01-fcs 
// See <a href="http://java.sun.com/xml/jaxb">http://java.sun.com/xml/jaxb</a> 
// Any modifications to this file will be lost upon recompilation of the source schema. 
// Generated on: 2006.08.17 at 04:09:29 PM PDT 
//


package org.flowcyt.facejava.transformation.jaxb;

import javax.xml.bind.annotation.XmlAccessType;
import javax.xml.bind.annotation.XmlAccessorType;
import javax.xml.bind.annotation.XmlAttribute;
import javax.xml.bind.annotation.XmlType;


/**
 * 
 * 				Abstract type to be used as a common parent for pre-defined transformations using
 * 				- the r constant as the analog-to-digital resolution
 * 				- the d constant asthe number of decades for the dynamic range of parameter
 * 			
 * 
 * <p>Java class for Abstract-r-d-Transformation complex type.
 * 
 * <p>The following schema fragment specifies the expected content contained within this class.
 * 
 * <pre>
 * &lt;complexType name="Abstract-r-d-Transformation">
 *   &lt;complexContent>
 *     &lt;extension base="{http://www.isac-net.org/std/Transformation-ML/v1.0/}AbstractPredefinedTransformation">
 *       &lt;attribute name="d" use="required" type="{http://www.isac-net.org/std/common-types/v1.0/}PositiveDouble" />
 *       &lt;attribute name="r" use="required" type="{http://www.isac-net.org/std/common-types/v1.0/}PositiveDouble" />
 *     &lt;/extension>
 *   &lt;/complexContent>
 * &lt;/complexType>
 * </pre>
 * 
 * 
 */
@XmlAccessorType(XmlAccessType.FIELD)
@XmlType(name = "Abstract-r-d-Transformation", namespace = "http://www.isac-net.org/std/Transformation-ML/v1.0/")
public abstract class AbstractRDTransformation
    extends AbstractPredefinedTransformation
{

    @XmlAttribute(namespace = "http://www.isac-net.org/std/Transformation-ML/v1.0/", required = true)
    protected double d;
    @XmlAttribute(namespace = "http://www.isac-net.org/std/Transformation-ML/v1.0/", required = true)
    protected double r;

    /**
     * Gets the value of the d property.
     * 
     */
    public double getD() {
        return d;
    }

    /**
     * Sets the value of the d property.
     * 
     */
    public void setD(double value) {
        this.d = value;
    }

    /**
     * Gets the value of the r property.
     * 
     */
    public double getR() {
        return r;
    }

    /**
     * Sets the value of the r property.
     * 
     */
    public void setR(double value) {
        this.r = value;
    }

}
