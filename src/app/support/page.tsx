"use client";

import { SignInButton, SignedIn, SignedOut, UserButton } from "@clerk/nextjs";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Textarea } from "@/components/ui/textarea";
import { Label } from "@/components/ui/label";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { 
  Mail, 
  MessageCircle, 
  Phone, 
  HelpCircle, 
  FileText, 
  ExternalLink,
  Send,
  ArrowLeft
} from "lucide-react";
import { ThemeToggle } from "@/components/theme-toggle";
import Image from "next/image";
import Link from "next/link";
import { useState } from "react";

export default function SupportPage() {
  const [contactForm, setContactForm] = useState({
    name: "",
    email: "",
    subject: "",
    message: ""
  });

  const handleFormChange = (field: string, value: string) => {
    setContactForm(prev => ({
      ...prev,
      [field]: value
    }));
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    // Here you would typically send the form data to your backend
    console.log("Support form submitted:", contactForm);
    alert("Thank you for your message! We'll get back to you soon.");
    setContactForm({ name: "", email: "", subject: "", message: "" });
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-indigo-50 via-white to-cyan-50 dark:from-gray-900 dark:via-gray-800 dark:to-gray-900">
      {/* Header */}
      <div className="py-6 px-4 border-b bg-white/50 dark:bg-gray-800/50 backdrop-blur-sm">
        <div className="container mx-auto max-w-5xl flex items-center justify-between">
          <div className="flex items-center gap-4">
            <Link href="/">
              <Button variant="ghost" size="sm">
                <ArrowLeft className="w-4 h-4 mr-2" />
                Back to Home
              </Button>
            </Link>
            <div className="flex items-center gap-3">
              <Image
                src="/codeguide-logo.png"
                alt="CodeGuide Logo"
                width={40}
                height={40}
                className="rounded-lg"
              />
              <h1 className="text-2xl font-bold bg-gradient-to-r from-blue-600 via-blue-500 to-blue-400 bg-clip-text text-transparent font-parkinsans">
                Support Center
              </h1>
            </div>
          </div>
          
          <div className="flex items-center gap-3">
            <ThemeToggle />
            <SignedOut>
              <SignInButton>
                <Button size="sm">Sign In</Button>
              </SignInButton>
            </SignedOut>
            <SignedIn>
              <UserButton />
            </SignedIn>
          </div>
        </div>
      </div>

      <main className="container mx-auto px-4 py-8 max-w-5xl">
        {/* Welcome Section */}
        <div className="text-center mb-8">
          <h2 className="text-3xl font-bold mb-4">How can we help you?</h2>
          <p className="text-lg text-muted-foreground max-w-2xl mx-auto">
            Find answers to common questions, contact our support team, or explore our documentation.
          </p>
        </div>

        <Tabs defaultValue="faq" className="space-y-6">
          <TabsList className="grid w-full grid-cols-3">
            <TabsTrigger value="faq">FAQ</TabsTrigger>
            <TabsTrigger value="contact">Contact Us</TabsTrigger>
            <TabsTrigger value="resources">Resources</TabsTrigger>
          </TabsList>

          {/* FAQ Tab */}
          <TabsContent value="faq" className="space-y-4">
            <div className="grid gap-4">
              <Card>
                <CardHeader>
                  <CardTitle className="flex items-center gap-2">
                    <HelpCircle className="w-5 h-5" />
                    Frequently Asked Questions
                  </CardTitle>
                  <CardDescription>
                    Quick answers to the most common questions
                  </CardDescription>
                </CardHeader>
                <CardContent className="space-y-6">
                  <div>
                    <h4 className="font-semibold mb-2">How do I get started with the CodeGuide Starter Kit?</h4>
                    <p className="text-muted-foreground">
                      Follow the setup guide on the home page to configure your environment variables for Clerk, Supabase, and AI providers. 
                      Check the SUPABASE_CLERK_SETUP.md file for detailed integration instructions.
                    </p>
                  </div>
                  
                  <div>
                    <h4 className="font-semibold mb-2">What authentication providers are supported?</h4>
                    <p className="text-muted-foreground">
                      We use Clerk for authentication, which supports Google, GitHub, email/password, and many other providers. 
                      You can configure these in your Clerk dashboard.
                    </p>
                  </div>
                  
                  <div>
                    <h4 className="font-semibold mb-2">How do I customize the theme and styling?</h4>
                    <p className="text-muted-foreground">
                      The project uses TailwindCSS v4 with shadcn/ui components. You can customize colors in the CSS custom properties 
                      in globals.css, and the theme system supports both light and dark modes automatically.
                    </p>
                  </div>
                  
                  <div>
                    <h4 className="font-semibold mb-2">Can I use different AI providers?</h4>
                    <p className="text-muted-foreground">
                      Yes! The Vercel AI SDK supports multiple providers. Set your OPENAI_API_KEY or ANTHROPIC_API_KEY 
                      environment variables to enable AI chat functionality.
                    </p>
                  </div>
                  
                  <div>
                    <h4 className="font-semibold mb-2">How does database security work?</h4>
                    <p className="text-muted-foreground">
                      We use Supabase Row Level Security (RLS) policies that integrate with Clerk user IDs via JWT tokens. 
                      This ensures users can only access their own data automatically.
                    </p>
                  </div>
                </CardContent>
              </Card>
            </div>
          </TabsContent>

          {/* Contact Tab */}
          <TabsContent value="contact" className="space-y-6">
            <div className="grid md:grid-cols-2 gap-6">
              {/* Contact Form */}
              <Card>
                <CardHeader>
                  <CardTitle className="flex items-center gap-2">
                    <MessageCircle className="w-5 h-5" />
                    Send us a message
                  </CardTitle>
                  <CardDescription>
                    Fill out the form below and we&apos;ll get back to you as soon as possible
                  </CardDescription>
                </CardHeader>
                <CardContent>
                  <form onSubmit={handleSubmit} className="space-y-4">
                    <div className="space-y-2">
                      <Label htmlFor="name">Name</Label>
                      <Input
                        id="name"
                        value={contactForm.name}
                        onChange={(e) => handleFormChange("name", e.target.value)}
                        placeholder="Your full name"
                        required
                      />
                    </div>
                    
                    <div className="space-y-2">
                      <Label htmlFor="email">Email</Label>
                      <Input
                        id="email"
                        type="email"
                        value={contactForm.email}
                        onChange={(e) => handleFormChange("email", e.target.value)}
                        placeholder="your.email@example.com"
                        required
                      />
                    </div>
                    
                    <div className="space-y-2">
                      <Label htmlFor="subject">Subject</Label>
                      <Input
                        id="subject"
                        value={contactForm.subject}
                        onChange={(e) => handleFormChange("subject", e.target.value)}
                        placeholder="What's this about?"
                        required
                      />
                    </div>
                    
                    <div className="space-y-2">
                      <Label htmlFor="message">Message</Label>
                      <Textarea
                        id="message"
                        value={contactForm.message}
                        onChange={(e) => handleFormChange("message", e.target.value)}
                        placeholder="Describe your issue or question in detail..."
                        className="min-h-[120px]"
                        required
                      />
                    </div>
                    
                    <Button type="submit" className="w-full">
                      <Send className="w-4 h-4 mr-2" />
                      Send Message
                    </Button>
                  </form>
                </CardContent>
              </Card>

              {/* Contact Methods */}
              <div className="space-y-6">
                <Card>
                  <CardHeader>
                    <CardTitle>Other ways to reach us</CardTitle>
                    <CardDescription>
                      Choose the method that works best for you
                    </CardDescription>
                  </CardHeader>
                  <CardContent className="space-y-4">
                    <div className="flex items-center gap-3 p-3 rounded-lg bg-muted/50">
                      <Mail className="w-5 h-5 text-blue-500" />
                      <div>
                        <p className="font-medium">Email Support</p>
                        <p className="text-sm text-muted-foreground">support@codeguide.dev</p>
                      </div>
                    </div>
                    
                    <div className="flex items-center gap-3 p-3 rounded-lg bg-muted/50">
                      <MessageCircle className="w-5 h-5 text-green-500" />
                      <div>
                        <p className="font-medium">Live Chat</p>
                        <p className="text-sm text-muted-foreground">Available Mon-Fri, 9AM-5PM EST</p>
                      </div>
                    </div>
                    
                    <div className="flex items-center gap-3 p-3 rounded-lg bg-muted/50">
                      <Phone className="w-5 h-5 text-purple-500" />
                      <div>
                        <p className="font-medium">Phone Support</p>
                        <p className="text-sm text-muted-foreground">+1 (555) 123-4567</p>
                      </div>
                    </div>
                  </CardContent>
                </Card>

                <Card>
                  <CardHeader>
                    <CardTitle>Response Times</CardTitle>
                  </CardHeader>
                  <CardContent className="space-y-3">
                    <div className="flex justify-between">
                      <span className="text-sm">General Inquiries</span>
                      <span className="text-sm font-medium">24-48 hours</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-sm">Technical Issues</span>
                      <span className="text-sm font-medium">12-24 hours</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-sm">Urgent Support</span>
                      <span className="text-sm font-medium">2-4 hours</span>
                    </div>
                  </CardContent>
                </Card>
              </div>
            </div>
          </TabsContent>

          {/* Resources Tab */}
          <TabsContent value="resources" className="space-y-6">
            <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6">
              <Card>
                <CardHeader>
                  <CardTitle className="flex items-center gap-2">
                    <FileText className="w-5 h-5" />
                    Documentation
                  </CardTitle>
                  <CardDescription>
                    Comprehensive guides and API references
                  </CardDescription>
                </CardHeader>
                <CardContent>
                  <div className="space-y-3">
                    <Button variant="outline" className="w-full justify-start" asChild>
                      <Link href="#" onClick={() => window.open("https://nextjs.org/docs", "_blank")}>
                        <ExternalLink className="w-4 h-4 mr-2" />
                        Next.js Documentation
                      </Link>
                    </Button>
                    <Button variant="outline" className="w-full justify-start" asChild>
                      <Link href="#" onClick={() => window.open("https://clerk.com/docs", "_blank")}>
                        <ExternalLink className="w-4 h-4 mr-2" />
                        Clerk Auth Docs
                      </Link>
                    </Button>
                    <Button variant="outline" className="w-full justify-start" asChild>
                      <Link href="#" onClick={() => window.open("https://supabase.com/docs", "_blank")}>
                        <ExternalLink className="w-4 h-4 mr-2" />
                        Supabase Docs
                      </Link>
                    </Button>
                  </div>
                </CardContent>
              </Card>

              <Card>
                <CardHeader>
                  <CardTitle className="flex items-center gap-2">
                    <MessageCircle className="w-5 h-5" />
                    Community
                  </CardTitle>
                  <CardDescription>
                    Connect with other developers
                  </CardDescription>
                </CardHeader>
                <CardContent>
                  <div className="space-y-3">
                    <Button variant="outline" className="w-full justify-start" asChild>
                      <Link href="#" onClick={() => window.open("https://github.com/your-repo/discussions", "_blank")}>
                        <ExternalLink className="w-4 h-4 mr-2" />
                        GitHub Discussions
                      </Link>
                    </Button>
                    <Button variant="outline" className="w-full justify-start" asChild>
                      <Link href="#" onClick={() => window.open("https://discord.gg/codeguide", "_blank")}>
                        <ExternalLink className="w-4 h-4 mr-2" />
                        Discord Community
                      </Link>
                    </Button>
                    <Button variant="outline" className="w-full justify-start" asChild>
                      <Link href="#" onClick={() => window.open("https://twitter.com/codeguide", "_blank")}>
                        <ExternalLink className="w-4 h-4 mr-2" />
                        Follow on Twitter
                      </Link>
                    </Button>
                  </div>
                </CardContent>
              </Card>

              <Card>
                <CardHeader>
                  <CardTitle className="flex items-center gap-2">
                    <HelpCircle className="w-5 h-5" />
                    Quick Links
                  </CardTitle>
                  <CardDescription>
                    Helpful resources and tools
                  </CardDescription>
                </CardHeader>
                <CardContent>
                  <div className="space-y-3">
                    <Button variant="outline" className="w-full justify-start" asChild>
                      <Link href="/">
                        <ArrowLeft className="w-4 h-4 mr-2" />
                        Back to Dashboard
                      </Link>
                    </Button>
                    <Button variant="outline" className="w-full justify-start" asChild>
                      <Link href="#" onClick={() => window.open("https://ui.shadcn.com/docs", "_blank")}>
                        <ExternalLink className="w-4 h-4 mr-2" />
                        shadcn/ui Components
                      </Link>
                    </Button>
                    <Button variant="outline" className="w-full justify-start" asChild>
                      <Link href="#" onClick={() => window.open("https://tailwindcss.com/docs", "_blank")}>
                        <ExternalLink className="w-4 h-4 mr-2" />
                        TailwindCSS Docs
                      </Link>
                    </Button>
                  </div>
                </CardContent>
              </Card>
            </div>
          </TabsContent>
        </Tabs>
      </main>
    </div>
  );
}