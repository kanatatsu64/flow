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
    _values 'flow name' $(flow flow-list | tr '\n' ' ')
}

function _feature_name(){
    _values 'fearute name' $(flow feature-list | tr '\n' ' ')
}

compdef _flow_completion flow