function QuestionAccordion({ questions }) {
    return (
      <div>
        {questions.map((q, index) => (
          <Question key={index} question={q.question} answer={q.answer} />
        ))}
      </div>
    );
  }
  
  function Question({ question, answer }) {
    const [isOpen, setIsOpen] = useState(false);
  
    return (
      <div>
        <button onClick={() => setIsOpen(!isOpen)}>{question}</button>
        {isOpen && <p>{answer}</p>}
      </div>
    );
  }
  