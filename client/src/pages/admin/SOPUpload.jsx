import { useState, useEffect } from 'react' 
import { useAuth } from '../../state/authContext' 

export default function SOPUpload() { 
  const { isAuthenticated } = useAuth() 
  const [file, setFile] = useState(null) 
  const [isUploading, setIsUploading] = useState(false) 
  const [message, setMessage] = useState('') 
  const [isError, setIsError] = useState(false) 
  const [currentSOP, setCurrentSOP] = useState(null) 

  useEffect(() => { 
    fetchSOPStatus() 
  }, []) 

  const fetchSOPStatus = async () => { 
    try { 
      const res = await fetch( 
        'http://localhost:8000/api/v1/admin/sop-status', 
        { 
          credentials: 'include' 
        } 
      ) 
      const data = await res.json() 
      if (data.exists) { 
        setCurrentSOP(data) 
      } 
    } catch (err) { 
      console.error('SOP status error:', err) 
    } 
  } 

  const handleUpload = async () => { 
    if (!file) { 
      setMessage('Please select a PDF file first') 
      setIsError(true) 
      return 
    } 
    setIsUploading(true) 
    setMessage('') 
    try { 
      const formData = new FormData() 
      formData.append('file', file) 
      const res = await fetch( 
        'http://localhost:8000/api/v1/admin/sop-upload', 
        { 
          method: 'POST', 
          credentials: 'include', 
          body: formData 
        } 
      ) 
      const data = await res.json() 
      if (data.success) { 
        setMessage('SOP uploaded successfully! Chatbot will now use this document.') 
        setIsError(false) 
        setFile(null) 
        fetchSOPStatus() 
      } else { 
        setMessage('Upload failed: ' + (data.detail || 'Unknown error')) 
        setIsError(true) 
      } 
    } catch (err) { 
      setMessage('Upload failed: ' + err.message) 
      setIsError(true) 
    } finally { 
      setIsUploading(false) 
    } 
  } 

  return ( 
    <div className="p-6 max-w-2xl mx-auto"> 
      <h1 className="text-2xl font-bold text-gray-800 mb-2"> 
        SOP Document Upload 
      </h1> 
      <p className="text-gray-500 mb-6"> 
        Upload your company SOP PDF. 
        The chatbot will use this document 
        to answer user questions. 
      </p> 

      {currentSOP && ( 
        <div className="bg-green-50 border border-green-200 
                        rounded-lg p-4 mb-6"> 
          <p className="text-green-700 font-medium"> 
            ✅ Current SOP Document: 
          </p> 
          <p className="text-green-600 text-sm mt-1"> 
            📄 {currentSOP.filename} 
          </p> 
          <p className="text-green-500 text-xs mt-1"> 
            Uploaded: {new Date( 
              currentSOP.uploaded_at 
            ).toLocaleDateString()} 
          </p> 
        </div> 
      )} 

      <div className="bg-white border-2 border-dashed 
                      border-gray-300 rounded-lg p-8 
                      text-center mb-4"> 
        <p className="text-gray-400 mb-4"> 
          📄 Select PDF file to upload 
        </p> 
        <input 
          type="file" 
          accept=".pdf" 
          onChange={(e) => { 
            setFile(e.target.files[0]) 
            setMessage('') 
          }} 
          className="block mx-auto text-sm text-gray-500" 
        /> 
        {file && ( 
          <p className="text-blue-600 text-sm mt-2"> 
            Selected: {file.name} 
          </p> 
        )} 
      </div> 

      <button 
        onClick={handleUpload} 
        disabled={isUploading || !file} 
        className="w-full bg-blue-600 text-white 
                   py-3 px-6 rounded-lg font-medium 
                   hover:bg-blue-700 disabled:opacity-50 
                   disabled:cursor-not-allowed" 
      > 
        {isUploading ? 'Uploading...' : 'Upload SOP Document'} 
      </button> 

      {message && ( 
        <div className={`mt-4 p-3 rounded-lg text-sm 
          ${isError 
            ? 'bg-red-50 text-red-600 border border-red-200' 
            : 'bg-green-50 text-green-600 border border-green-200' 
          }`}> 
          {message} 
        </div> 
      )} 
    </div> 
  ) 
} 
