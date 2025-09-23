import { Card, CardContent, CardFooter, CardHeader, CardTitle } from '@/components/ui/card';
import { Input } from '@/components/ui/input';
import { Button } from '@/components/ui/button';
import { ScrollArea } from '@/components/ui/scroll-area';
import { Avatar, AvatarFallback, AvatarImage } from '@/components/ui/avatar';
import { BrainCircuit, Paperclip, Send } from 'lucide-react';

export default function AiTutorPage() {
  return (
    <div className="flex flex-col items-center">
      <div className="text-center mb-8">
        <h1 className="text-4xl font-headline font-bold">AI Tutor</h1>
        <p className="text-muted-foreground mt-2">Your personal physics assistant.</p>
      </div>

      <Card className="w-full max-w-3xl h-[70vh] flex flex-col">
        <CardHeader className="flex flex-row items-center justify-between">
          <div className="flex items-center space-x-4">
            <Avatar>
              <AvatarImage src="https://picsum.photos/100/100" data-ai-hint="robot" />
              <AvatarFallback>AI</AvatarFallback>
            </Avatar>
            <div>
              <CardTitle className="text-lg">PhysicsAI</CardTitle>
              <p className="text-sm text-muted-foreground">Online</p>
            </div>
          </div>
        </CardHeader>
        <CardContent className="flex-grow flex flex-col relative">
            <div className="absolute inset-0 bg-background/80 backdrop-blur-sm flex flex-col items-center justify-center z-10 rounded-lg">
                <BrainCircuit className="h-16 w-16 text-primary mb-4" />
                <h2 className="text-2xl font-bold">AI Tutor is Coming Soon!</h2>
                <p className="text-muted-foreground mt-2">Get ready for an interactive learning experience.</p>
            </div>
          <ScrollArea className="h-full pr-4">
            <div className="space-y-4">
              <ChatMessage author="AI" text="Hello! I am PhysicsAI, your personal tutor. What concept can I help you understand today?" />
              <ChatMessage author="You" text="Can you explain Newton's Second Law of Motion?" />
               <ChatMessage author="AI" text="Of course! Newton's Second Law states that the acceleration of an object is directly proportional to the net force acting upon it and inversely proportional to its mass (F=ma). This means..." />
            </div>
          </ScrollArea>
        </CardContent>
        <CardFooter className="pt-4 border-t">
          <div className="flex w-full items-center space-x-2">
            <Button variant="ghost" size="icon" className="flex-shrink-0" disabled>
              <Paperclip className="h-5 w-5" />
            </Button>
            <Input placeholder="Type your message..." disabled />
            <Button className="bg-accent hover:bg-accent/90" disabled>
              <Send className="h-5 w-5" />
            </Button>
          </div>
        </CardFooter>
      </Card>
    </div>
  );
}

function ChatMessage({ author, text }: { author: string, text: string }) {
  const isUser = author === 'You';
  return (
    <div className={`flex items-end gap-2 ${isUser ? 'justify-end' : 'justify-start'}`}>
      {!isUser && (
        <Avatar className="h-8 w-8">
            <AvatarImage src="https://picsum.photos/100/100" data-ai-hint="robot" />
          <AvatarFallback>AI</AvatarFallback>
        </Avatar>
      )}
      <div className={`max-w-xs md:max-w-md rounded-lg px-4 py-2 ${isUser ? 'bg-primary text-primary-foreground' : 'bg-muted'}`}>
        <p className="text-sm">{text}</p>
      </div>
      {isUser && (
        <Avatar className="h-8 w-8">
          <AvatarImage />
          <AvatarFallback>You</AvatarFallback>
        </Avatar>
      )}
    </div>
  );
}
