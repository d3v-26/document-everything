#!/usr/bin/env nextflow
nextflow.enable.dsl=2

workflow {
    Channel.fromPath(params.input) | PROCESS_A
}

process PROCESS_A {
    input: path reads
    output: path "*.txt"
    script:
    """
    echo "Processing ${reads}" > output.txt
    """
}
