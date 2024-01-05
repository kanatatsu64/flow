#compdef _flow_completion flow

function _flow_completion(){
    _arguments '1: :->command' '2: :->args'

    case $state in
        command)
            _values 'subcommand' 'init' 'start' 'checkout' 'delete' 'feature-list' 'flow-list' 'push' 'rebase'
            ;;
        args)
            case $line[1] in
                init)
                    _flow_name
                    ;;
                start)
                    _flow_name
                    ;;
                checkout)
                    _feature_name
                    ;;
                delete)
                    _feature_name
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

compdef _flow_completion flow