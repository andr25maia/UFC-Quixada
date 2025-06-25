const AlunoModel = require("../models/aluno.model.js"); 
const alunos = require("../data/aluno.js"); 

let id = 2;
class AlunoService {

    static listar() {
        return alunos;
   }

    static buscarPorId(id) {
        return alunos.find(aluno => aluno.id === id);
    }

    static criar(aluno) {
        id++;
        const novoAluno = new AlunoModel();
        novoAluno.id = id;
        novoAluno.nome = aluno.nome;
        novoAluno.curso = aluno.curso;
        novoAluno.ira = aluno.ira;
        alunos.push(novoAluno);
        return novoAluno;
    }

  static atualizar(id, {nome, ira, curso}) {
        for(let i=0; i<alunos.length; i++) {
            if(alunos[i].id == id){
                alunos[i].nome = nome
                alunos[i].ira = ira
                alunos[i].curso = curso 
                return alunos[i]
            }
        }
        return null
    }

    static excluir(id) {
        const index = alunos.findIndex(aluno => aluno.id === id);
        if (index !== -1) {
            alunos.splice(index, 1);
            return true;
        }
        return false;
    }

  static recuperar(id) {
        for(let i=0; i<alunos.length; i++) {
            if(alunos[i].id == id) return alunos[i]
        }
        return null
    }

}
module.exports = AlunoService;