const importantTasks = ['submission', 'quiz', 'skill', 'contest', 'preparation', 'prepare', 'checkup', 'study',
                        'final', 'job', 'exam']
const notImportantTasks = ['hangout', 'movie', 'series', 'gossip', 'fun']
 

function findInCat(element) {
    const cat = document.getElementById('category')
    for (let i = 0; i < cat.options.length; i++) {
        if (element === cat.options[i].value) {
            return cat.options[i].value
        }
    }
    return 'other'
}; 

document.getElementById('task-text').addEventListener('keyup', ()=>{
    let taskText = document.getElementById('task-text').value.toLowerCase()
    let matched = false
    importantTasks.forEach(element => {
        if (taskText.includes(element)) {
            matched = true
            let ctr = findInCat(element)
            document.getElementById('category').value = ctr
            document.getElementById('importance').value = 'high'
            document.getElementById('importance').disabled = false
            return true
        }
    });

    notImportantTasks.forEach(element => {
        if (taskText.includes(element)) {
            matched = true
            let ctr = findInCat(element)
            document.getElementById('category').value = ctr
            document.getElementById('importance').value = 'low'
            document.getElementById('importance').disabled = false
            return true
        }
    });

    if (!matched) {
        document.getElementById('category').value = ""
        document.getElementById('importance').value = ''
        document.getElementById('importance').disabled = true
    }
});

document.getElementById('category').addEventListener("change", ()=>{
    let type = document.getElementById('category').value
    let imp = document.getElementById('importance')
    if (type === 'other') {
        imp.disabled = false;
    } else {
        imp.value = ''
        imp.disabled = true;
    }
});
