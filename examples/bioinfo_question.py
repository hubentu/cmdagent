from cmdagent.mcp_api import mcp_api

mcp = mcp_api(host='0.0.0.0', port=8000)
mcp.add_tool('examples/ensembl_symbol.cwl', 'ensembl_symbol')
mcp.add_tool('examples/bcftools_view.cwl', 'bcftools_view', read_outs=False)
mcp.serve()

# Question: What is the genome coordinates of the gene "BRCA1"?
# Question: Is there any variant in the gene "BRCA1" from the https://ftp.ncbi.nlm.nih.gov/pub/clinvar/vcf_GRCh38/clinvar.vcf.gz?