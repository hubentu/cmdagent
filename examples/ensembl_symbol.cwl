cwlVersion: v1.0
class: CommandLineTool
baseCommand:
- sh
- script.sh
requirements:
- class: InitialWorkDirRequirement
  listing:
  - entryname: script.sh
    entry: |2

      curl -s -H 'Content-Type:application/json' 'https://rest.ensembl.org/lookup/symbol/'$1/$2
    writable: false
- class: DockerRequirement
  dockerPull: curlimages/curl
label: Find gene name, id, description, canonical transcript and genome location for
  a gene symbol in a linked external database
inputs:
  species:
    label: species
    type: string?
    inputBinding:
      position: 1
      separate: true
    default: homo_sapiens
  symbol:
    label: gene symbol
    type: string
    inputBinding:
      position: 2
      separate: true
outputs:
  out:
    type: stdout
