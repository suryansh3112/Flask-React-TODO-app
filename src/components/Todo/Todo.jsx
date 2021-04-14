import React, {useState, useEffect} from 'react'
import axios from 'axios'
import { Input, Button } from 'antd';

import {EditFilled, DeleteFilled} from '@ant-design/icons'
import './todo.css'

function Todo() {

  const[task, setTask] = useState("");
  const[update, setUpdate] = useState({
    status:false,
    todo:{},
    upd:""
  });
  
  const[todos,setTodos] = useState([])

  useEffect(() => {
    const func = async ()=>{
      const token = localStorage.getItem('auth-token')
      const res = await axios.get('/api',{ headers: { 'Authorization': 'Bearer '+token } })
      setTodos(res.data);
    }

    func();
    
  }, [])

  const save = async()=>{

    const data = {content:task}
    const token = localStorage.getItem('auth-token')
    const res = await axios.post('/add',data,{ headers: { 'Authorization': 'Bearer '+token } })
    if(res.status===201){       
      setTodos(prev=>[...prev,res.data]);
      setTask("")
    }
  }

  const updateTask = async()=>{
    const temp = update
    const idx = todos.findIndex((t)=> temp.todo.id===t.id)

    console.log("temp",temp,"\nidx",idx)
    const token = localStorage.getItem('auth-token')
    const res = await axios.patch(`/update/${temp.todo.id}`,{content:temp.upd},{ headers: { 'Authorization': 'Bearer '+token } })

    console.log(res.status);
    if(res.status===200){
      setTodos(prev=>{
        let n = prev;
        n[idx] = res.data;
        return n;
      })

      setUpdate({
        status:false,
        todo:{},
        upd:""
      })
    }


    
  }

  const deleteTask = async(id)=>{
    
    try {
      const token = localStorage.getItem('auth-token')
      await axios.delete(`/delete/${id}`,{ headers: { 'Authorization': 'Bearer '+token } })
      setTodos((prev)=>{
        const res = prev.filter((cur)=>cur.id!==id)
        return res;
      })
    } catch (error) {
      console.error(error);
      alert('Something went wrong. Please try again.')
    }
    
  }

  return (
    <div className='todo'> 
      <div className='input'>
        {update.status ? 
        <>
        <Input placeholder="Enter Task" name='upd' value={update.upd} onChange={e=>setUpdate(prev=>{
          
          return {
            ...prev,
            upd:e.target.value
          }
        })}/>
          <Button type="primary" onClick={()=>updateTask()} >Update</Button>
        </>
        :
        <>
          <Input placeholder="Enter Task" name='task' value={task} onChange={e=>setTask(e.target.value)}/>
          <Button type="primary" onClick={()=>save()} >Save</Button>
        </>
        }
      </div>
      
      <div>
        {todos && todos.map(todo=>{
          return (
            <div className='list'>
              <div className='text'>
                {todo.content}
              </div>
              <div className='todo-btn-list'>
                <Button className='todo-btn' style={{marginRight:'10px'}} type='primary' onClick={()=>{setUpdate({status:true,todo:todo,upd:todo.content})}}><EditFilled /></Button>
                <Button className='todo-btn' type='danger' onClick={()=>deleteTask(todo.id)}><DeleteFilled /></Button>
              </div>
            </div>
          )
        })}
      </div>

    </div>
  )
}

export default Todo
