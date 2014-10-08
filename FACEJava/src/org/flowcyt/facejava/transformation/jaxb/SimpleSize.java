//
// This file was generated by the JavaTM Architecture for XML Binding(JAXB) Reference Implementation, v2.0.2-b01-fcs 
// See <a href="http://java.sun.com/xml/jaxb">http://java.sun.com/xml/jaxb</a> 
// Any modifications to this file will be lost upon recompilation of the source schema. 
// Generated on: 2006.08.17 at 04:09:29 PM PDT 
//


package org.flowcyt.facejava.transformation.jaxb;

import javax.xml.bind.annotation.XmlEnum;
import javax.xml.bind.annotation.XmlEnumValue;


/**
 * <p>Java class for simple-size.
 * 
 * <p>The following schema fragment specifies the expected content contained within this class.
 * <p>
 * <pre>
 * &lt;simpleType name="simple-size">
 *   &lt;restriction base="{http://www.w3.org/2001/XMLSchema}string">
 *     &lt;enumeration value="small"/>
 *     &lt;enumeration value="normal"/>
 *     &lt;enumeration value="big"/>
 *   &lt;/restriction>
 * &lt;/simpleType>
 * </pre>
 * 
 */
@XmlEnum
public enum SimpleSize {

    @XmlEnumValue("small")
    SMALL("small"),
    @XmlEnumValue("normal")
    NORMAL("normal"),
    @XmlEnumValue("big")
    BIG("big");
    private final String value;

    SimpleSize(String v) {
        value = v;
    }

    public String value() {
        return value;
    }

    public static SimpleSize fromValue(String v) {
        for (SimpleSize c: SimpleSize.values()) {
            if (c.value.equals(v)) {
                return c;
            }
        }
        throw new IllegalArgumentException(v.toString());
    }

}
