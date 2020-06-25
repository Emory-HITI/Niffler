<xsl:stylesheet version="1.0" xmlns:xsl="http://www.w3.org/1999/XSL/Transform">
  <xsl:output method="text"/>

  <xsl:template match="/NativeDicomModel">
    <xsl:text>"</xsl:text>
    <xsl:apply-templates select="DicomAttribute[@tag='0020000D']"/>
    <xsl:text>"</xsl:text>
    <xsl:text>,</xsl:text>
    <xsl:text>"</xsl:text>
    <xsl:apply-templates select="DicomAttribute[@tag='00100020']"/>
    <xsl:text>"</xsl:text>
  </xsl:template>

  <xsl:template match="DicomAttribute">
    <xsl:apply-templates select="Value"/>
  </xsl:template>

  <xsl:template match="Value">
    <xsl:if test="@number != 1">\</xsl:if>
    <xsl:value-of select="text()"/>
  </xsl:template>

</xsl:stylesheet>
