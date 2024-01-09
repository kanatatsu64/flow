#compdef _flow_completion flow

function _flow_completion(){
    _arguments '1: :->command' '*: :->args'

    case $state in
        command)
            _values 'subcommand' 'init' 'start' 'checkout' 'delete' 'feature-list' 'flow-list' 'diff' 'push' 'rebase' 'reset'
            ;;
        args)
            case $line[1] in
                init)
                    _arguments '2: :_init_flow_name' '3: :_init_base_branch'
                    ;;
                start)
                    _arguments '2: :_flow_name'
                    ;;
                checkout)
                    _arguments '2: :_feature_name'
                    ;;
                delete)
                    _arguments '2: :_feature_name'
                    ;;
                diff)
                    _arguments '*: :_diff_options'
                    ;;
            esac
            ;; 
    esac
}

function _flow_name(){
    local -a list
    list=($(flow flow-list | tr '\n' ' '))
    [[ !  -z  $list  ]] &&  _values 'flow name' $list
}

function _feature_name(){
    local -a list
    list=($(flow feature-list | tr '\n' ' '))
    [[ !  -z  $list  ]] &&  _values 'flow name' $list
}

function _init_flow_name(){
    local -a flow_list
    local -a candidate_list
    local -a list
    flow_list=($(flow flow-list))
    candidate_list=($(git branch --list "develop/*" | sed 's/^[* ] //' | sed 's/^develop\///'))
    list=($(echo -e "${candidate_list}\n${flow_list}" | uniq))
    [[ !  -z  $list  ]] &&  _values 'flow name' $list
}

function _init_base_branch(){
    local -a list
    list=($(git branch --list "*$line[2]" | sed 's/^[* ] //' | tr '\n' ' '))
    [[ !  -z  $list  ]] &&  _values 'base branch' $list
}

function _diff_options(){
    _values 'option' '--test' '--oneline'
}

compdef _flow_completion flow