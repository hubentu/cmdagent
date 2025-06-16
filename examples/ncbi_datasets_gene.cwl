cwlVersion: v1.2
class: CommandLineTool
baseCommand:
- datasets
- summary
- gene
- symbol
requirements:
- class: DockerRequirement
  dockerPull: staphb/ncbi-datasets
- class: NetworkAccess
  networkAccess: true
label: Print a summary of a gene dataset
inputs:
  gene:
    doc: The gene symbol to retrieve metadata
    type: string
    inputBinding:
      position: 1
      separate: true
  taxon:
    doc: spiece taxon, such as human, mus musculus
    type: string?
    inputBinding:
      position: 2
      prefix: --taxon
      separate: true
outputs:
  json:
    doc: metadata in JSON format
    type: stdout
