cwlVersion: v1.2
class: CommandLineTool
baseCommand:
- bcftools
- view
requirements:
- class: DockerRequirement
  dockerPull: quay.io/biocontainers/bcftools:1.13--h3a49de5_0
- class: NetworkAccess
  networkAccess: true
label: bcftools_view
doc: VCF/BCF conversion, view, subset and filter VCF/BCF files.
inputs:
  vcf:
    label: vcf
    doc: Input VCF file
    type:
    - File
    - string
    inputBinding:
      separate: true
  filter:
    label: filter
    doc: require at least one of the listed FILTER strings (e.g. 'PASS,.')
    type: string?
    inputBinding:
      prefix: -f
      separate: true
  fout:
    label: fout
    doc: output file name
    type: string
    inputBinding:
      prefix: -o
      separate: true
  otype:
    label: otype
    doc: 'b: compressed BCF, u: uncompressed BCF, z: compressed VCF, v: uncompressed
      VCF [v]'
    type: string?
    inputBinding:
      prefix: -O
      separate: true
    default: v
  sample:
    label: sample
    doc: comma separated list of samples to include (or exclude with '^' prefix)
    type: string?
    inputBinding:
      prefix: -s
      separate: true
  samplefile:
    label: samplefile
    doc: file of samples to include (or exclude with '^' prefix)
    type: File?
    inputBinding:
      prefix: -S
      separate: true
  genotype:
    label: genotype
    doc: require one or more hom/het/missing genotype or, if prefixed with '^', exclude
      sites with hom/het/missing genotypes
    type: string?
    inputBinding:
      prefix: -g
      separate: true
  include:
    label: include
    doc: select sites for which the expression is true
    type: string?
    inputBinding:
      prefix: -i
      separate: true
  exclude:
    label: exclude
    doc: exclude sites for which the expression is true
    type: string?
    inputBinding:
      prefix: -e
      separate: true
  region:
    label: region
    doc: The genome region (chr:beginPos-endPos) to subset
    type: string?
    inputBinding:
      position: 99
      separate: true
outputs:
  Fout:
    label: Fout
    doc: Viewed,filtered,.subsetted vcf file output
    type: File
    outputBinding:
      glob: $(inputs.fout)
$rud:
  author: rworkflow team
  date: 09-08-24
  url: https://github.com/samtools/bcftools
  example: []
