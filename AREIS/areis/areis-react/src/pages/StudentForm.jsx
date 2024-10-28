import React, { useState, useEffect } from 'react';
import { useSearchParams } from 'react-router-dom';

const StudentForm = () => {
  const [responses, setResponses] = useState({
    content1: '',
    content2: '',
    content3: '',
    content4: '',
    content5: '',
    content6: '',
    content7: '',
    content8: '',
    content9: '',
  });
  const [checkboxes, setCheckboxes] = useState({
    option1: false,
    option2: false,
    option3: false,
  });
  const [error, setError] = useState(null);
  const [formSubmitted, setFormSubmitted] = useState(false);
  const [loading, setLoading] = useState(true);
  const [studentId, setStudentId] = useState(null);

  const [searchParams] = useSearchParams();

  useEffect(() => {
    const fetchFormData = async () => {
      const studentIdParam = searchParams.get('studentId');
      console.log("Fetching data for student ID:", studentIdParam); // Debug log
      if (!studentIdParam) {
        setError('Student ID is missing');
        setLoading(false);
        return;
      }

      setStudentId(studentIdParam);

      try {
        const requestUrl = `/managestudents/api/student-form/?studentId=${studentIdParam}`;
        console.log("Request URL:", requestUrl); // Debug log
        const response = await fetch(requestUrl);

        if (!response.ok) throw new Error('Failed to fetch form data');
        
        const data = await response.json();
        console.log("Fetched data:", data); // Debug log
        if (data.error) {
          setError(data.error);
        } else if (data.formSubmitted) {
          setFormSubmitted(true);
        } else {
          setResponses({
            content1: data.content1 || '',
            content2: data.content2 || '',
            content3: data.content3 || '',
            content4: data.content4 || '',
            content5: data.content5 || '',
            content6: data.content6 || '',
            content7: data.content7 || '',
            content8: data.content8 || '',
            content9: data.content9 || ''
          });
        }
      } catch (err) {
        console.error('Error fetching form data:', err);
        setError('Failed to load form data.');
      } finally {
        setLoading(false);
      }
    };

    fetchFormData();
  }, [searchParams]);

  const handleChange = (question, value) => {
    setResponses(prevResponses => ({
      ...prevResponses,
      [question]: value,
    }));
  };

  const handleCheckboxChange = (option) => {
    setCheckboxes(prevCheckboxes => ({
      ...prevCheckboxes,
      [option]: !prevCheckboxes[option],
    }));
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    
    try {
      const response = await fetch('/managestudents/api/student-form/', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          student_id: studentId,
          ...responses,
          ...checkboxes
        }),
      });

      if (!response.ok) {
        const errorText = await response.text();
        throw new Error(`HTTP error! status: ${response.status}, body: ${errorText}`);
      }

      const data = await response.json();
      
      if (data.error) {
        throw new Error(data.error);
      }

      setFormSubmitted(true);
    } catch (err) {
      console.error('Error submitting form:', err);
      setError(`Failed to submit form: ${err.message}`);
    }
  };

  const questions = [
    "I understand the course materials.",
    "I have sufficient knowledge from previous studies to progress in the course.",
    "I have difficulties with concentrating or staying focused while studying.",
    "I manage my time effectively to meet deadlines and complete assignments.",
    "I have difficulty understanding English.",
    "My overall stress level is high.",
    "I have health issues (physical or mental) that impact my studies.",
    "I have difficulties balancing other commitments (e.g., work, family).",
    "I have financial issues.",
  ];

  const checkboxOptions = [
    "Course Content",
    "Learning Issues",
    "Personal",
  ];

  console.log("Component state - loading:", loading, "formSubmitted:", formSubmitted, "error:", error); // Debugging output for state

  if (loading) {
    return (
      <div className="flex justify-center items-center min-h-screen">
        <div className="text-xl font-semibold text-gray-600">Loading form...</div>
      </div>
    );
  }

  if (formSubmitted) {
    return (
      <div className="max-w-lg mx-auto p-6 bg-white shadow-md rounded-lg mt-8">
        <div className="text-center text-lg text-green-600">
          Thank you! Your form has been successfully submitted.
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="max-w-lg mx-auto p-6 bg-white shadow-md rounded-lg mt-8">
        <div className="text-center text-lg text-red-600">
          {error}
        </div>
      </div>
    );
  }

  return (
    <form onSubmit={handleSubmit} className="max-w-lg mx-auto p-6 bg-white shadow-md rounded-lg mt-8">
      <h1 className="text-3xl font-semibold mb-6 text-center">Student Form</h1>
      
      {questions.map((question, index) => (
        <div key={index} className="mb-6">
          <label className="block text-lg font-medium mb-2">{question}</label>
          <div className="flex justify-around">
            {[1, 2, 3, 4, 5].map((value) => (
              <label key={value} className="flex flex-col items-center">
                <input
                  type="radio"
                  name={`content${index + 1}`}
                  value={value}
                  checked={responses[`content${index + 1}`] === value}
                  onChange={() => handleChange(`content${index + 1}`, value)}
                  className="hidden"
                />
                <span className={`flex items-center justify-center w-10 h-10 rounded-full border-2 cursor-pointer ${
                  responses[`content${index + 1}`] === value 
                    ? 'border-blue-500 bg-blue-100 text-blue-600' 
                    : 'border-gray-300'
                } transition duration-200`}>
                  {value}
                </span>
              </label>
            ))}
          </div>
        </div>
      ))}

      <h2 className="text-lg font-semibold mb-4">Additional Options:</h2>
      <div className="flex justify-between mb-6">
        {checkboxOptions.map((option, index) => (
          <label key={index} className="flex items-center cursor-pointer">
            <input
              type="checkbox"
              checked={checkboxes[`option${index + 1}`]}
              onChange={() => handleCheckboxChange(`option${index + 1}`)}
              className="hidden"
            />
            <span className={`flex items-center justify-center w-32 h-10 rounded-lg border-2 cursor-pointer transition duration-200 
              ${checkboxes[`option${index + 1}`] ? 'bg-blue-500 text-white border-blue-500' : 'bg-gray-200 border-gray-400'}
              hover:bg-blue-400 hover:text-white`}>
              {option}
            </span>
          </label>
        ))}
      </div>

      <button 
        type="submit" 
        className="w-full bg-blue-500 text-white py-3 rounded-lg hover:bg-blue-600 transition duration-200"
      >
        Submit
      </button>
    </form>
  );
};

export default StudentForm;
